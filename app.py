from flask import Flask, render_template, request, redirect, url_for
from werkzeug.utils import secure_filename
import os

thisDir = os.path.dirname(os.path.abspath(__file__))
g = {}
app = Flask(__name__)


@app.route('/', methods=['POST', 'GET'])
def upload():
    if request.method == 'POST':
        global g
        d = request.form['code']
        f = request.files['file']
        e = d + '.jpg'
        upload_path = "%s/static/%s.jpg" % (thisDir, d)
        f.save(upload_path)
        if g.get(d):
            a = g.get(d)
            g[d] = "nothing"
            return a
        else:
            g[d] = "nothing"
            return g[d]
    return render_template("index.html")


@app.route('/key', methods=['POST', 'GET'])
def ccmd():
    if request.method == 'POST':
        global g
        a = request.values['code']
        g[a] = request.values['keey']
        print(a, g)
    return ""


@app.route("/finish", methods=['POST', 'GET'])
def finish_cmd():
    print(request.values.get("data"))
    return "success"


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
