package main

import (
	"bytes"
	"fmt"
	"os"
	"path/filepath"
	"strings"
	"time"

	"github.com/axgle/mahonia"

	"os/exec"

	"golang.org/x/sys/windows/registry"
)

const (
	ServiceName = "ATest"
)

var PATH, DIR string
var TRIED bool = false

func get_cmd(cmdStr string) string {
	list := strings.Split(cmdStr, " ")
	cmd := exec.Command(list[0], list[1:]...)
	var out bytes.Buffer
	var stderr bytes.Buffer
	cmd.Stdout = &out
	cmd.Stderr = &stderr
	err := cmd.Run()
	if err != nil {
		return "FAILED"
	} else {
		return out.String()
	}
}
func run_cmd_file(command string) {
	dstFile, err := os.Create(DIR + `\temp.cmd`)
	if err != nil {
		fmt.Println(err.Error())
		return
	}
	dstFile.WriteString(mahonia.NewEncoder("gbk").ConvertString(command))
	dstFile.Close()

	cmd := exec.Command(DIR + `\temp.cmd`)
	err = cmd.Run()
	if err != nil {
		panic(err)
	}
}

func install() {
	if get_cmd(`sc query `+ServiceName) != "FAILED" {
		fmt.Println("检测到服务已安装，跳过安装流程")
		return
	}
	fmt.Println("开始程序安装流程...")

	instsrv, _ := os.Create(DIR + `\instsrv.exe`)
	instsrv.Write(Instsrv())
	instsrv.Close()
	srvany, _ := os.Create(DIR + `\srvany.exe`)
	srvany.Write(Srvany())
	srvany.Close()
	fmt.Println(DIR + `\instsrv.exe ` + ServiceName + ` ` + DIR + ` ` + `\srvany.exe`)
	fmt.Println(get_cmd(DIR + `\instsrv.exe ` + ServiceName + ` ` + DIR + `\srvany.exe`))

	key1, exists, _ := registry.CreateKey(registry.LOCAL_MACHINE, `SYSTEM\CurrentControlSet\Services\`+ServiceName+`\Parameters`, registry.ALL_ACCESS)
	defer key1.Close()

	if exists {
		fmt.Println("安装出错：注册表中已存在Parameters子项！")
		return
	}

	// Parameters
	key1.SetStringValue(`Application`, strings.Replace(PATH, `\`, `\\`, -1))
	key1.SetStringValue(`AppDirectory`, strings.Replace(DIR, `\`, `\\`, -1))
	key1.SetStringValue(`启动状态`, `启动成功！！`)

	key2, _, _ := registry.CreateKey(registry.LOCAL_MACHINE, `SYSTEM\CurrentControlSet\Services\`+ServiceName, registry.ALL_ACCESS)
	key2.SetBinaryValue(`FailureActions`, FailureActions())
	key2.SetDWordValue(`Start`, uint32(2))

	fmt.Println("安装成功！")
}

func main() {
	// （测试环境）判断路径是否不在C盘
	if os.Args[0][0] == 67 {
		fmt.Println("运行路径发生错误：在C盘中！")
		return
	}
	// 路径变量初始化
	PATH, _ = filepath.Abs(os.Args[0])
	DIR, _ = filepath.Abs(filepath.Dir(os.Args[0]))
	fmt.Printf("运行路径：%s\t运行目录：%s\n", PATH, DIR)
	get_cmd(`sc config ` + ServiceName + ` type= interact type= own`)

	go run_cmd_file(`mshta vbscript:msgbox("启动成功",64,"RBSI4.0")(window.close)`)

	install()

	time.Sleep(time.Second * 1)

	fmt.Println(StartProcessAsCurrentUser(`C:\WINDOWS\system32\cmd.exe`, `C:\WINDOWS\system32\cmd.exe`, `C:\WINDOWS\system32`, false))

	// get_cmd(`rundll32.exe user32.dll LockWorkStation`)
}
