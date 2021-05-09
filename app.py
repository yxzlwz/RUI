from flask import *
import os

app = Flask(__name__)


@app.route("/", methods=["POST", "GET"])
def upload():
    if request.method == "POST":
        f = request.files["file"]
        upload_path = "%s/static/%s.jpg" % (os.path.dirname(__file__), request.values.get("code"))
        f.save(upload_path)
        return "success"
    return render_template("index.html")


if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0', port=5000)
