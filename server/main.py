from flask import Flask, abort, request

app = Flask(__name__)

@app.route("/")
def index_page():
    return "<title>HackBlogger</title>"

if __name__ == "__main__":
    app.run()