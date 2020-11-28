package main

import (
	"bytes"
	"fmt"
	"net"
	"time"
	"unicode/utf16"
)

func string2utf16be(s string) []byte {
	shorts := utf16.Encode([]rune(s))
	result := make([]byte, len(shorts)*2)
	for i, v := range shorts {
		result[i*2] = byte(v >> 8)
		result[i*2+1] = byte(v & 255)
	}

	return result
}

func utf16be2string(b []byte) string {
	shorts := make([]uint16, len(b)>>1)
	for i := range shorts {
		shorts[i] = (uint16(b[i*2]) << 8) | uint16(b[i*2+1])
	}
	return string(utf16.Decode(shorts))
}

func check(realhost string, host string, port uint32, result chan string) {
	defer func() {
		fmt.Println(recover())
		close(result)
	}()

	checkError := func(err error) {
		if err != nil {
			panic(err)
		}
	}

	timeout := time.Second
	conn, err := net.DialTimeout("tcp", realhost, timeout)
	checkError(err)

	err = conn.SetDeadline(time.Now().Add(timeout))
	checkError(err)

	buffer := new(bytes.Buffer)
	_, err = buffer.Write([]byte("\xFE\x01\xFA\x00\x0B"))
	checkError(err)

	// TODO: rewrite efficiently?
	_, err = buffer.Write(string2utf16be("MC|PingHost"))
	checkError(err)

	hostname := string2utf16be(host)
	length1 := len(hostname)
	length2 := len(hostname) + 7

	_, err = buffer.Write([]byte{byte(length2 >> 8), byte(length2 & 255), 0x4a, byte(length1 >> 8), byte(length1 & 255)})
	checkError(err)

	_, err = buffer.Write(hostname)
	checkError(err)

	_, err = buffer.Write([]byte{byte(port >> 24), byte((port >> 16) & 255), byte((port >> 8) & 255), byte(port & 255)})
	checkError(err)

	_, err = conn.Write(buffer.Bytes())
	checkError(err)

	outBuffer := new(bytes.Buffer)
	outTmp := make([]byte, 1024)

	for {
		i, err := conn.Read(outTmp)
		if err == nil {
			_, err = outBuffer.Write(outTmp[:i])
			checkError(err)
		} else {
			break
		}
	}

	tmp := outBuffer.Bytes()

	result <- utf16be2string(tmp[3:])
}

func main() {
	result := make(chan string)
	go check("mc.hypixel.net:25565", "127.0.0.1", 25565, result)
	h, more := <-result
	if more {
		fmt.Println(h)
	} else {
		fmt.Println("Got nothing.")
	}
}
