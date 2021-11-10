package main

import (
	"fmt"
	"image/png"
	"os"

	"github.com/kbinani/screenshot"

)

func main() {
	img, _ := screenshot.CaptureRect(screenshot.GetDisplayBounds(0))
	file, _ := os.Create(os.Args[1])
	png.Encode(file, img)
	file.Close()
	fmt.Println("截图成功！")
}
