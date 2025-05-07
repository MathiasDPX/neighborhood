from flask import Blueprint, render_template, send_file, request
import requests

endpoint = "http://127.0.0.1:5000"

site = Blueprint('site', __name__,
                        template_folder='templates')

@site.route("/favicon.ico", methods=["GET"])
def favicon():
    return send_file("static/img/favicon.ico")

@site.route("/article/<id>")
def article(id:int):
    headers = {
        "Authorization": request.headers.get("Authorization")
    }
    data = requests.get(f"{endpoint}/api/article/{id}").json()
    userdata = requests.get(f"{endpoint}/api/user/data", headers=headers)
    return render_template("article.html",
                            data=data, userdata=userdata)

@site.route("/user/<id>")
def user(id:int):
    data = requests.get(f"{endpoint}/api/user/{id}").json()
    articles = requests.get(f"{endpoint}/api/user/{id}/articles").json()
    return render_template("user.html", data=data, articles=articles)

@site.route('/', methods=["GET"])
def index():
    return render_template("index.html")