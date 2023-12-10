"""
wordengine_discord_show: server.py
データを扱うサーバープログラムです。
"""

import math
import json
import hashlib
import urllib.request
import xmltodict
import hashlib

from flask import Flask, jsonify, request, Response
from flask_cors import CORS
from flask_jwt_extended import jwt_required, create_access_token, JWTManager, get_jwt_identity

# config_read
json_open = open('../config.json', 'r', encoding='UTF-8')
json_load = json.load(json_open)

JWT_SECRET_KEY = json_load['JWT_SECRET_KEY']
user_name = json_load['user_name']

# Password_Hash
hash_password = hashlib.sha256(json_load['password'].encode()).hexdigest()

app = Flask(__name__)
app.config["JWT_SECRET_KEY"] = f'{JWT_SECRET_KEY}'
jwt = JWTManager(app)
CORS(app)
id_dict = {f'{user_name}': f'{hash_password}'} #ユーザー名とパスワードのsha256ハッシュ
class Data():
    """ キャッシュと再生状態を記録するクラス """
    status = {f'{user_name}': {"status": "closed"}}
    cache = {}


def jwt_unauthorized_loader_handler(_):
    return jsonify({"msg": "unauthorized"}), "401 Unauthorized"
jwt.unauthorized_loader(jwt_unauthorized_loader_handler)

@app.route("/login", methods=["POST"])
def login():
    if request.content_type.split(";")[0] == "application/json": # 送られてきた認証情報の形式を確認
        data = request.json
    elif request.content_type.split(";")[0] == "text/plain": # Content-typeをapplication/jsonにするとCORSの関係で送れなくなるブラウザのためにtext/plainにも対応する
        data = json.loads(request.data)
    else:
        return jsonify({"msg": "bad content-type"}), "415 Unsupported media type"
    try:
        if data["user"] in id_dict: # 該当ユーザーが存在するか検証する
            if data["password"] == id_dict[data["user"]]: # 送られてきたパスワードがもともとハッシュ値で、そのまま認証データと比較できる場合やってしまう
                user = data["user"]
            else:
                pwhash = hashlib.sha256() # 送られてきたパスワードがハッシュ値でなくても認証するために送られてきたパスワードをハッシュ値にしてからもう一度比較する
                pwhash.update(data["password"].encode())
                if pwhash.hexdigest() == id_dict[data["user"]]:
                    user = data["user"]
                else:
                    return jsonify({"msg": "Unauthorized"}), "401 Unauthorized"
        else:
            return jsonify({"msg": "Unauthorized"}), "401 Unauthorized"
    except KeyError:
        return jsonify({"msg": "Unprocessable json"}), "400 Bad request" # ユーザーとパスワードのどちらかがなかった場合400を返す
    token = create_access_token(identity=user)
    return jsonify({"msg": "ok", "token": token}), "200 OK"

@app.route("/status", methods=["POST", "GET"])
@jwt_required()
def status():
    """ API /status: 状態記録・取得API """
    if request.method == "POST":
        if request.content_type.split(";")[0] == "application/json":
            data = request.json
        elif request.content_type.split(";")[0] == "text/plain":
            data = json.loads(request.data)
        else:
            return jsonify({"msg": "bad content-type"}), "415 Unsupported media type"
        try:
            if data["status"] == "closed":
                Data.status[get_jwt_identity()] = {"status": data["status"]}
                return jsonify({"msg": "success"}), "201 Created"
            if data["status"] == "my_page":
                Data.status[get_jwt_identity()] = {"status": data["status"], "daily_progress": data["daily_progress"], "daily_goal": data['daily_goal'], "weekly_progress": data['weekly_progress'], "weekly_goal": data['weekly_goal'], "ranking": data['ranking']}
            if data["status"] == "studyreport":
                Data.status[get_jwt_identity()] = {"status": data["status"], "daily_progress": data["daily_progress"], "daily_goal": data['daily_goal'], "weekly_progress": data['weekly_progress'], "weekly_goal": data['weekly_goal'], "ranking": data['ranking']}
            if data["status"] == "flashwords":
                Data.status[get_jwt_identity()] = {"status": data["status"], "progress": data['progress']}
            if data["status"] == "wordpanic":
                Data.status[get_jwt_identity()] = {"status": data["status"]}
        except KeyError:
            print(data)
            return jsonify({"msg": "missing value"}), "400 Bad Request"
        return jsonify({"msg": "success"}), "201 Created"
    elif request.method == "GET":
        return jsonify(Data.status[get_jwt_identity()]), "200 OK"

if __name__ == "__main__":
    app.run(debug=True)

