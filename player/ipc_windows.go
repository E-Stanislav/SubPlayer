//go:build windows

package player

import (
	"errors"
	"net"
	"time"

	"gopkg.in/natefinch/npipe.v2"
)

func dialIPC(ipcPath string) (net.Conn, error) {
	type res struct {
		c   net.Conn
		err error
	}
	ch := make(chan res, 1)
	go func() {
		c, err := npipe.Dial(ipcPath)
		ch <- res{c: c, err: err}
	}()

	select {
	case r := <-ch:
		return r.c, r.err
	case <-time.After(800 * time.Millisecond):
		return nil, errors.New("ipc dial timeout")
	}
}


