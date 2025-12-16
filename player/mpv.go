package player

import (
	"bufio"
	"bytes"
	"encoding/json"
	"errors"
	"fmt"
	"net"
	"os"
	"os/exec"
	"path/filepath"
	"runtime"
	"sync"
	"time"
)

type MPVPlayer struct {
	mu sync.Mutex

	cmd *exec.Cmd

	// ipc
	ipcPath string
	conn    net.Conn
	br      *bufio.Reader

	reqID int
}

func NewMPVPlayer() *MPVPlayer {
	return &MPVPlayer{}
}

func (p *MPVPlayer) CheckBackend() error {
	_, err := exec.LookPath("mpv")
	if err != nil {
		return err
	}
	return nil
}

func (p *MPVPlayer) Open(path string) error {
	p.mu.Lock()
	defer p.mu.Unlock()

	if err := p.ensureClosedLocked(); err != nil {
		return err
	}

	if _, err := exec.LookPath("mpv"); err != nil {
		return errors.New("mpv не найден в PATH")
	}

	ipc, err := p.makeIPCPath()
	if err != nil {
		return err
	}
	p.ipcPath = ipc

	args := []string{
		"--force-window=yes",
		"--idle=no",
		"--keep-open=no",
		"--terminal=no",
		"--input-ipc-server=" + p.ipcPath,
		"--msg-level=ipc=v",
		"--",
		path,
	}

	cmd := exec.Command("mpv", args...)
	// Keep mpv detached from current terminal; suppress stdio noise.
	cmd.Stdout = nil
	cmd.Stderr = nil
	cmd.Stdin = nil

	if err := cmd.Start(); err != nil {
		_ = p.cleanupIPCLocked()
		return err
	}
	p.cmd = cmd

	// Connect to IPC (wait a bit for mpv to create socket)
	deadline := time.Now().Add(2 * time.Second)
	for {
		if time.Now().After(deadline) {
			_ = p.ensureClosedLocked()
			return errors.New("не удалось подключиться к mpv IPC (таймаут)")
		}
		c, err := dialIPC(p.ipcPath)
		if err == nil {
			p.conn = c
			p.br = bufio.NewReader(p.conn)
			break
		}
		time.Sleep(50 * time.Millisecond)
	}

	// Set some defaults
	_ = p.SetVolume(100)
	return nil
}

func (p *MPVPlayer) Close() error {
	p.mu.Lock()
	defer p.mu.Unlock()
	return p.ensureClosedLocked()
}

func (p *MPVPlayer) Stop() error {
	// "quit" closes mpv process
	_ = p.command([]any{"quit"})
	return p.Close()
}

func (p *MPVPlayer) TogglePause() error {
	return p.SetProperty("pause", "cycle")
}

func (p *MPVPlayer) SeekRelative(sec int) error {
	return p.command([]any{"seek", sec, "relative"})
}

func (p *MPVPlayer) SeekAbsolute(sec int) error {
	return p.command([]any{"seek", sec, "absolute"})
}

func (p *MPVPlayer) SetVolume(v int) error {
	return p.SetProperty("volume", v)
}

func (p *MPVPlayer) Duration() (int, error) {
	val, err := p.GetProperty("duration")
	if err != nil {
		return 0, err
	}
	f, ok := val.(float64)
	if !ok {
		return 0, errors.New("duration: unexpected type")
	}
	return int(f + 0.5), nil
}

func (p *MPVPlayer) TimePos() (int, error) {
	val, err := p.GetProperty("time-pos")
	if err != nil {
		return 0, err
	}
	f, ok := val.(float64)
	if !ok {
		return 0, errors.New("time-pos: unexpected type")
	}
	return int(f + 0.5), nil
}

func (p *MPVPlayer) SetProperty(name string, value any) error {
	// special "cycle" helper for toggles
	if s, ok := value.(string); ok && s == "cycle" {
		return p.command([]any{"cycle", name})
	}
	return p.command([]any{"set_property", name, value})
}

func (p *MPVPlayer) GetProperty(name string) (any, error) {
	res, err := p.commandWithReply([]any{"get_property", name})
	if err != nil {
		return nil, err
	}
	return res.Data, nil
}

type mpvReq struct {
	Command   []any `json:"command"`
	RequestID int   `json:"request_id"`
}

type mpvResp struct {
	RequestID int             `json:"request_id"`
	Error     string          `json:"error"`
	Data      json.RawMessage `json:"data"`
}

type reply struct {
	Data any
}

func (p *MPVPlayer) command(cmd []any) error {
	_, err := p.commandWithReply(cmd)
	// Some commands don't reply if connection is gone; treat as best-effort.
	if errors.Is(err, net.ErrClosed) {
		return nil
	}
	return err
}

func (p *MPVPlayer) commandWithReply(cmd []any) (*reply, error) {
	p.mu.Lock()
	defer p.mu.Unlock()

	if p.conn == nil {
		return nil, errors.New("mpv не запущен")
	}

	p.reqID++
	req := mpvReq{Command: cmd, RequestID: p.reqID}
	b, _ := json.Marshal(req)
	b = append(b, '\n')

	if _, err := p.conn.Write(b); err != nil {
		return nil, err
	}

	// mpv replies line-delimited JSON; it can also emit async "event" messages.
	_ = p.conn.SetReadDeadline(time.Now().Add(900 * time.Millisecond))
	var resp mpvResp
	for i := 0; i < 20; i++ {
		line, err := p.br.ReadBytes('\n')
		if err != nil {
			return nil, err
		}
		line = bytes.TrimSpace(line)
		if len(line) == 0 {
			continue
		}
		if err := json.Unmarshal(line, &resp); err != nil {
			// ignore garbage
			continue
		}
		if resp.RequestID != req.RequestID {
			// likely an event message; ignore
			continue
		}
		if resp.Error != "success" && resp.Error != "" {
			return nil, fmt.Errorf("mpv error: %s", resp.Error)
		}
		break
	}

	// decode data if present
	if len(resp.Data) == 0 || string(resp.Data) == "null" {
		return &reply{Data: nil}, nil
	}
	var v any
	if err := json.Unmarshal(resp.Data, &v); err != nil {
		// If mpv returns something odd, just return raw
		return &reply{Data: string(resp.Data)}, nil
	}
	return &reply{Data: v}, nil
}

func (p *MPVPlayer) ensureClosedLocked() error {
	if p.conn != nil {
		_ = p.conn.Close()
		p.conn = nil
		p.br = nil
	}

	if p.cmd != nil && p.cmd.Process != nil {
		_ = p.cmd.Process.Kill()
		_, _ = p.cmd.Process.Wait()
		p.cmd = nil
	}

	return p.cleanupIPCLocked()
}

func (p *MPVPlayer) cleanupIPCLocked() error {
	if p.ipcPath == "" {
		return nil
	}
	defer func() { p.ipcPath = "" }()

	// Windows named pipe: nothing to remove
	if runtime.GOOS == "windows" {
		return nil
	}
	_ = os.Remove(p.ipcPath)
	return nil
}

func (p *MPVPlayer) makeIPCPath() (string, error) {
	if runtime.GOOS == "windows" {
		// mpv expects \\.\pipe\name
		return `\\.\pipe\subplayer-mpv-ipc`, nil
	}

	dir, err := os.MkdirTemp("", "subplayer-mpv-*")
	if err != nil {
		return "", err
	}
	return filepath.Join(dir, "mpv.sock"), nil
}
