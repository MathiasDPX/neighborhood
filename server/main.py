import os
from psycopg2.errors import *
from dotenv import load_dotenv
from datetime import timedelta
from flask import Flask, jsonify, request, redirect, abort
from flask_jwt_extended import create_access_token, get_jwt_identity, jwt_required, JWTManager, set_access_cookies
from scss_manager import *
from website import site
import requests
import database

load_dotenv()

app = Flask(__name__)

app.config["JWT_SECRET_KEY"] = os.getenv("secret", "please.add.a.secret")
app.config["JWT_TOKEN_LOCATION"] = ["cookies", "headers"]
app.config["JWT_COOKIE_SECURE"] = not (__name__ == "__main__")
app.config["JWT_COOKIE_CSRF_PROTECT"] = not (__name__ == "__main__")
jwt = JWTManager(app)

#app.register_blueprint(site)
#app.register_blueprint(scss_manager)
#compile_scss()

SLACK_CLIENT_ID = os.getenv("SLACK_CLIENT_ID")
SLACK_CLIENT_SECRET = os.getenv("SLACK_CLIENT_SECRET")
SLACK_REDIRECT_URI = os.getenv("SLACK_REDIRECT_URI", "http://localhost:5000/api/auth/slack/callback")
SLACK_OAUTH_URL = f"https://slack.com/oauth/v2/authorize?client_id={SLACK_CLIENT_ID}&user_scope=identity.avatar,identity.basic,identity.email&redirect_uri={SLACK_REDIRECT_URI}"

"""Slack OAuth"""
@app.route("/api/auth/slack", methods=["GET"])
def slack_login():
    if not SLACK_CLIENT_ID:
        return jsonify({"success": False, "message": "Slack OAuth not configured"}), 500
    return redirect(SLACK_OAUTH_URL)

"""OAuth callback"""
# MARK: OAuth
@app.route("/api/auth/slack/callback")
def slack_callback():
    code = request.args.get("code")
    error = request.args.get("error")
    
    if error:
        return jsonify({"success": False, "message": f"Slack authorization error: {error}"}), 400
    
    if not code:
        return jsonify({"success": False, "message": "Authorization code is missing"}), 400
    
    token_response = requests.post(
        "https://slack.com/api/oauth.v2.access",
        data={
            "client_id": SLACK_CLIENT_ID,
            "client_secret": SLACK_CLIENT_SECRET,
            "code": code,
            "redirect_uri": SLACK_REDIRECT_URI
        }
    ).json()
    
    if not token_response.get("ok", False):
        return jsonify({
            "success": False,
            "message": f"Failed to exchange code for token: {token_response.get('error')}"
        }), 400
    
    access_token = token_response.get("authed_user", {}).get("access_token")
    if not access_token:
        return jsonify({"success": False, "message": "No access token received"}), 400
        
    user_info_response = requests.get(
        "https://slack.com/api/users.identity",
        headers={"Authorization": f"Bearer {access_token}"}
    ).json()
    
    if not user_info_response.get("ok", False):
        return jsonify({
            "success": False, 
            "message": f"Failed to get user info: {user_info_response.get('error')}"
        }), 400
    
    slack_user_id = user_info_response.get("user", {}).get("id")
    slack_username = user_info_response.get("user", {}).get("name")

    user_id = database.User.get_userid_by_slack(slack_user_id)
    
    if not user_id:
        user_id = database.User.create_user(slack_user_id, slack_username)
    else:
        user_id = user_id[0]
    
    str_user_id = str(user_id)
    access_token = create_access_token(identity=str_user_id, expires_delta=timedelta(days=3))
    
    resp = jsonify({'success': True, 'message': 'Login successful'})
    set_access_cookies(resp, access_token)
    return resp, 200

# MARK: Users
valids_settings = {
    "username": str,
    "timezone": str,
    "bio": str,
    "github": str
}
"""Change user settings"""
@app.route("/api/user/settings", methods=["PUT"])
@jwt_required()
def change_settings():
    data = request.get_json()

    id = get_jwt_identity()
    key = data.get("key")
    val = data.get("value")

    if key == None or val == None:
        return {"success": False, "message": "Missing values (key, value)"}
    
    valtype = valids_settings.get(key)
    if valtype == None:
        return {"success": False, "message": f"Invalid key '{key}'"}
    
    if type(val) != valtype:
        return {"success": False, "message": f"Invalid value type (expected '{valtype}' got '{type(val)}')"}
    
    database.User.update_settings(id, key, val)
    return {"success": True}

"""Get public user data"""
@app.route("/api/user/<id>", methods=["GET"])
def user(id:int):
    settings = database.User.get_public_user(id)
    return settings

"""Retrieve user data"""
@app.route("/api/user/data", methods=["GET"])
@jwt_required(optional=None)
def get_userdata():
    identity = get_jwt_identity()
    if identity == None:
        return {"success": False}
    
    slack = database.User.get_slack(identity)
    if slack and slack[0]:
        slack_id = slack[0]
        response = requests.get(f"https://slack.mathias.hackclub.app/users.info/{slack_id}")
        pfp_url = response.json().get("user",{}).get("profile",{}).get("image_192", None)
        return {
            "success": True,
            "id": identity,
            "pfp": pfp_url
        }
    return {
        "success": False,
        "id": identity,
        "pfp": None
    }

#MARK: Articles
"""Get article data / Delete an article"""
@app.route("/api/article/<id>", methods=["GET", "DELETE"])
@jwt_required(optional=True)
def article(id:int):
    if request.method == "GET":
        data = database.Articles.get_pretty_article(id)
        return data
    elif request.method == "DELETE":
        article = database.Articles.get_article(id)
        if article.get("user", -1) != get_jwt_identity():
            abort(403)
        else:
            database.Articles.delete_article(id)

"""Post an article"""
@app.route("/api/articles/post", methods=["POST"])
@jwt_required()
def post_article():
    data = request.get_json()
    title = data.get("title")
    body = data.get("body")
    identity = get_jwt_identity()

    if title == None or body == None:
        return {"success": False, "message": "Missing values (title, body)"}

    try:
        id = database.Articles.post_article(identity, title, body)
        return {"success": True, "id":id}
    except:
        return {"success": False, "message": "Unable to save your article to database"}

"""Get someone articles"""
@app.route("/api/user/<id>/articles")
def user_articles(id:int):
    articles = database.Articles.get_user_articles(id)
    return jsonify(articles)

#MARK: Reviews
"""Get users reviews"""
@app.route("/api/user/<id>/reviews")
@jwt_required()
def user_reviews(id:int):
    limit = request.args.get("limit", 10, type=int)
    offset = request.args.get("offset", 0, type=int)
    
    return database.Reviews.get_user_reviews(id, limit=limit, offset=offset)

"""Post a review"""
@app.route("/api/article/<id>/review", methods=["POST", "GET"])
@jwt_required(optional=True)
def post_review(id:int):
    if request.method == "POST":
        data = request.get_json()
        note = data.get("note")
        comment = data.get("comment")
        identity = get_jwt_identity()

        if identity == None:
            abort(403)
            return

        if note == None or comment == None:
            return {"success": False, "message": "Missing values (note, comment)"}
        
        if note < 0 or note > 10:
            return {"success": False, "message": "Out of range note (between 0 and 10 inclusive)"}
        
        if len(comment) > 512:
            return {"success": False, "message": "Comment to long (512 max)"}
        
        try:
            database.Reviews.post_review(id, identity, comment, note)
        except UniqueViolation:
            return {"success": False, "message": "User already posted a review"}
        
        return {"success": True}
    elif request.method == "GET":
        limit = request.args.get("limit", 10, int)
        offset = request.args.get("offset", 0, int)
        return database.Reviews.get_reviews(id, offset, limit)

if __name__ == "__main__":
    app.run()