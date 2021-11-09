package main

import (
	"fmt"
	"os"
	"path/filepath"
	"strings"
	"time"

	"github.com/axgle/mahonia"

	"os/exec"

	"golang.org/x/sys/windows/registry"
)

func cmd(command, DIR string) {
	dstFile, err := os.Create("temp.cmd")
	if err != nil {
		fmt.Println(err.Error())
		return
	}
	dstFile.WriteString(mahonia.NewEncoder("gbk").ConvertString(command))
	dstFile.Close()

	cmd := exec.Command(DIR + `\\temp.cmd`)
	err = cmd.Run()
	if err != nil {
		panic(err)
	}
}

func main() {
	// 创建：指定路径的项
	// 路径：HKEY_CURRENT_USER\Software\Hello Go
	// alert()
	key, exists, _ := registry.CreateKey(registry.LOCAL_MACHINE, `SYSTEM\CurrentControlSet\Services\ATest\Parameters`, registry.ALL_ACCESS)
	defer key.Close()
	if os.Args[0][0] == 67 {
		fmt.Println("运行路径错误！")
		return
	}
	PATH, _ := filepath.Abs(os.Args[0])
	DIR, _ := filepath.Abs(filepath.Dir(os.Args[0]))
	fmt.Println("运行路径：", PATH, "    运行目录：", DIR)

	go cmd(`mshta vbscript:msgbox("我是提示内容",64,"我是提示标题")(window.close)`, DIR)

	// 判断是否已经存在了
	if exists {
		println(`键已存在`)
	} else {
		println(`新建注册表键`)
	}
	PATH = strings.Replace(PATH, `\`, `\\`, -1)
	DIR = strings.Replace(DIR, `\`, `\\`, -1)

	// 写入：32位整形值
	// key.SetDWordValue(`32位整形值`, uint32(123456))
	// 写入：64位整形值
	// key.SetQWordValue(`64位整形值`, uint64(123456))
	// 写入：字符串
	key.SetStringValue(`Application`, PATH)
	key.SetStringValue(`AppDirectory`, DIR)
	// key.SetStringValue(`启动状态`, `启动成功！`)

	// 写入：字符串数组
	// key.SetStringsValue(`字符串数组`, []string{`hello`, `world`})
	// 写入：二进制
	// key.SetBinaryValue(`二进制`, []byte{0x11, 0x22})

	// 读取：字符串
	// s, _, _ := key.GetStringValue(`ObjectName`)
	// println(s)
	// s, _, _ := key.GetBinaryValue("FailureActions")
	// fmt.Println(s)
	time.Sleep(time.Second)
}
