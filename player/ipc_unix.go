//go:build !windows

package player

import "net"

func dialIPC(ipcPath string) (net.Conn, error) {
	return net.Dial("unix", ipcPath)
}


