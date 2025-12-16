package main

import (
	"errors"
	"fmt"
	"path/filepath"
	"runtime"
	"strings"
	"time"

	"fyne.io/fyne/v2"
	"fyne.io/fyne/v2/app"
	"fyne.io/fyne/v2/container"
	"fyne.io/fyne/v2/dialog"
	"fyne.io/fyne/v2/layout"
	"fyne.io/fyne/v2/storage"
	"fyne.io/fyne/v2/theme"
	"fyne.io/fyne/v2/widget"

	"subplayer/player"
)

func main() {
	a := app.NewWithID("subplayer")
	w := a.NewWindow("SubPlayer")
	w.Resize(fyne.NewSize(820, 320))

	p := player.NewMPVPlayer()

	status := widget.NewLabel("Перетащи видео в окно или нажми Open.")
	fileLabel := widget.NewLabel("Файл не выбран")

	hasFile := false
	playing := false

	setPlayingUI := func(isPlaying bool, playAction *widget.ToolbarAction) {
		playing = isPlaying
		if playing {
			playAction.SetIcon(theme.MediaPauseIcon())
		} else {
			playAction.SetIcon(theme.MediaPlayIcon())
		}
	}

	updateStatus := func(s string) {
		status.SetText(s)
	}

	openPathBase := func(path string) {
		if path == "" {
			return
		}
		if runtime.GOOS == "windows" {
			// fyne on windows typically returns /C:/... form
			path = strings.TrimPrefix(path, "/")
		}
		if err := p.Open(path); err != nil {
			dialog.ShowError(err, w)
			return
		}
		hasFile = true
		fileLabel.SetText(filepath.Base(path))
		w.SetTitle("SubPlayer — " + filepath.Base(path))
		a.Preferences().SetString("lastDir", filepath.Dir(path))
		updateStatus("Воспроизведение: " + filepath.Base(path))
	}

	videoFilter := storage.NewExtensionFileFilter([]string{
		".mp4", ".mkv", ".mov", ".avi", ".webm", ".m4v", ".mpg", ".mpeg", ".wmv", ".flv",
	})

	var openPath func(string)

	showOpenDialog := func() {
		fd := dialog.NewFileOpen(func(rc fyne.URIReadCloser, err error) {
			if err != nil {
				dialog.ShowError(err, w)
				return
			}
			if rc == nil {
				return
			}
			defer rc.Close()
			openPath(rc.URI().Path())
		}, w)
		fd.SetFilter(videoFilter)
		fd.SetConfirmText("Open")
		if lastDir := a.Preferences().String("lastDir"); lastDir != "" {
			if u, err := storage.ListerForURI(storage.NewFileURI(lastDir)); err == nil {
				fd.SetLocation(u)
			}
		}
		fd.Resize(fyne.NewSize(980, 680))
		fd.Show()
	}

	vol := widget.NewSlider(0, 150)
	vol.SetValue(100)
	vol.Step = 1
	vol.OnChanged = func(v float64) {
		if !hasFile {
			return
		}
		_ = p.SetVolume(int(v))
	}
	volLabel := widget.NewLabelWithStyle("Volume", fyne.TextAlignLeading, fyne.TextStyle{Bold: true})

	seek := widget.NewSlider(0, 1000)
	seek.Step = 1
	posLabel := widget.NewLabel("--:--")
	durLabel := widget.NewLabel("--:--")
	seekTitle := widget.NewLabelWithStyle("Timeline", fyne.TextAlignLeading, fyne.TextStyle{Bold: true})
	seek.OnChangeEnded = func(v float64) {
		if !hasFile {
			return
		}
		// map 0..1000 to 0..duration
		d, err := p.Duration()
		if err != nil || d <= 0 {
			return
		}
		sec := (v / 1000.0) * float64(d)
		_ = p.SeekAbsolute(int(sec))
	}

	// Poll mpv for time/duration and update seek slider + label
	done := make(chan struct{})
	ticker := time.NewTicker(400 * time.Millisecond)
	defer ticker.Stop()
	go func() {
		for {
			select {
			case <-done:
				return
			case <-ticker.C:
				if !hasFile {
					continue
				}
				pos, _ := p.TimePos()
				dur, _ := p.Duration()
				if dur > 0 && pos >= 0 && !seek.Disabled() {
					seek.SetValue((float64(pos) / float64(dur)) * 1000.0)
					posLabel.SetText(fmtTime(pos))
					durLabel.SetText(fmtTime(dur))
				}
			}
		}
	}()

	hotkeys := widget.NewLabel("Горячие клавиши в окне mpv: Space (pause), ←/→ (seek), 9/0 (volume), f (fullscreen)")
	hotkeys.Wrapping = fyne.TextWrapWord

	// Toolbar (icons + disabled states)
	openAction := widget.NewToolbarAction(theme.FolderOpenIcon(), func() { showOpenDialog() })

	var playAction *widget.ToolbarAction
	var stopAction *widget.ToolbarAction
	var rewAction *widget.ToolbarAction
	var fwdAction *widget.ToolbarAction

	playAction = widget.NewToolbarAction(theme.MediaPlayIcon(), func() {
		if !hasFile {
			return
		}
		if err := p.TogglePause(); err != nil {
			dialog.ShowError(err, w)
			return
		}
		setPlayingUI(!playing, playAction)
		if playing {
			updateStatus("Play")
		} else {
			updateStatus("Pause")
		}
	})
	stopAction = widget.NewToolbarAction(theme.MediaStopIcon(), func() {
		if !hasFile {
			return
		}
		if err := p.Stop(); err != nil {
			dialog.ShowError(err, w)
			return
		}
		hasFile = false
		setPlayingUI(false, playAction)
		fileLabel.SetText("Файл не выбран")
		w.SetTitle("SubPlayer")
		seek.SetValue(0)
		posLabel.SetText("--:--")
		durLabel.SetText("--:--")
		updateStatus("Stop")

		// disable controls until next open
		playAction.Disable()
		stopAction.Disable()
		rewAction.Disable()
		fwdAction.Disable()
		seek.Disable()
	})
	rewAction = widget.NewToolbarAction(theme.MediaFastRewindIcon(), func() {
		if hasFile {
			_ = p.SeekRelative(-10)
		}
	})
	fwdAction = widget.NewToolbarAction(theme.MediaFastForwardIcon(), func() {
		if hasFile {
			_ = p.SeekRelative(10)
		}
	})

	toolbar := widget.NewToolbar(
		openAction,
		widget.NewToolbarSeparator(),
		rewAction,
		playAction,
		fwdAction,
		stopAction,
	)

	// Start disabled until a file is open
	playAction.Disable()
	stopAction.Disable()
	rewAction.Disable()
	fwdAction.Disable()
	seek.Disable()

	// Enable/disable when file opens/closes
	enableControls := func(enabled bool) {
		if enabled {
			playAction.Enable()
			stopAction.Enable()
			rewAction.Enable()
			fwdAction.Enable()
			seek.Enable()
		} else {
			playAction.Disable()
			stopAction.Disable()
			rewAction.Disable()
			fwdAction.Disable()
			seek.Disable()
		}
	}

	openPath = func(path string) {
		openPathBase(path)
		if hasFile {
			enableControls(true)
			setPlayingUI(true, playAction)
		}
	}

	// Nice “open” card
	openBig := widget.NewButtonWithIcon("Open video…", theme.FolderOpenIcon(), func() { showOpenDialog() })
	openBig.Importance = widget.HighImportance
	openCard := widget.NewCard(
		"Открыть видео",
		"Перетащи файл в окно или выбери его через диалог.",
		container.NewVBox(
			openBig,
			widget.NewSeparator(),
			widget.NewLabelWithStyle("Поддерживаются: mp4, mkv, mov, avi, webm…", fyne.TextAlignLeading, fyne.TextStyle{}),
		),
	)

	// Drag & drop on window
	w.SetOnDropped(func(_ fyne.Position, uris []fyne.URI) {
		if len(uris) == 0 {
			return
		}
		openPath(uris[0].Path())
	})

	// Menu (File -> Open / Quit)
	fileMenu := fyne.NewMenu("File",
		fyne.NewMenuItem("Open…", func() { showOpenDialog() }),
		fyne.NewMenuItemSeparator(),
		fyne.NewMenuItem("Quit", func() { w.Close() }),
	)
	w.SetMainMenu(fyne.NewMainMenu(fileMenu))

	header := container.NewVBox(
		toolbar,
		container.NewHBox(widget.NewLabelWithStyle("SubPlayer", fyne.TextAlignLeading, fyne.TextStyle{Bold: true}), layout.NewSpacer(), fileLabel),
	)

	timelineRow := container.NewBorder(nil, nil,
		container.NewHBox(posLabel),
		container.NewHBox(durLabel),
		seek,
	)

	controls := container.NewVBox(
		openCard,
		widget.NewSeparator(),
		seekTitle,
		timelineRow,
		container.NewHBox(volLabel, layout.NewSpacer(), vol),
		widget.NewSeparator(),
		status,
		hotkeys,
	)

	w.SetContent(container.NewPadded(container.NewBorder(header, nil, nil, nil, controls)))
	w.SetCloseIntercept(func() {
		close(done)
		_ = p.Close()
		w.Close()
	})

	// preflight check
	if err := p.CheckBackend(); err != nil {
		dialog.ShowError(errors.New("не найден mpv. Установи mpv и перезапусти.\n\n"+err.Error()), w)
	}

	w.ShowAndRun()
}

func fmtTime(sec int) string {
	if sec < 0 {
		return "--:--"
	}
	m := sec / 60
	s := sec % 60
	return fmt.Sprintf("%02d:%02d", m, s)
}
