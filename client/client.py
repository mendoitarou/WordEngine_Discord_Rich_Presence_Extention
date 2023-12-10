""" niconico2discord client program """
from __future__ import annotations

import datetime
import hashlib
import json
import time
import urllib.request

import pypresence
import xmltodict

# config_read
json_open = open('../config.json', 'r', encoding='UTF-8')
json_load = json.load(json_open)


CLIENT_ID = json_load['client_id']
password = json_load['password']
RPC = pypresence.Presence(CLIENT_ID)
RPC.connect()

class Auth():
    """ Class about Auth information """
    class User():
        """ Class about user information """
        def __init__(self, username: str, password: str):
            self.username = username
            self.password = hashlib.sha256()
            self.password.update(password.encode())
            self.password = self.password.hexdigest()
    class Token():
        """ JMT class """
        def __init__(self):
            self.token = ""
        def get(self, user: Auth.User):
            """ Get JMT from server """
            tokenrequest = urllib.request.Request("http://localhost:5000/login", headers={"Content-type": "application/json"}, data=json.dumps({"user": user.username, "password": user.password}).encode())
            self.token = json.load(urllib.request.urlopen(tokenrequest))["token"]

token = Auth.Token()
token.get(Auth.User(json_load['user_name'], password))

statusdata_request = urllib.request.Request("http://localhost:5000/status", headers={"Authorization": f"Bearer {token.token}"})
beforestatusdata = {}
beforeestimatedendtime = datetime.timedelta(seconds=0)
while True:
    try:
        statusdata = json.loads(urllib.request.urlopen(statusdata_request).read().decode())
    except urllib.error.HTTPError:
        token.get(Auth.User(json_load['user_name'], password))
        statusdata_request = urllib.request.Request("http://localhost:5000/status", headers={"Authorization": f"Bearer {token.token}"})
        continue
    if statusdata != beforestatusdata:
        print(statusdata)
        print(statusdata['status'])
        if statusdata['status'] == "closed":
            RPC.clear()
            beforestatusdata = statusdata
            continue
        elif statusdata['status'] == "my_page":
            url = "https://www.wordengine.jp/my_page.html"
            RPC.update(
                state=f"今日: {statusdata['daily_progress']}/{statusdata['daily_goal']} 今週: {statusdata['weekly_progress']}/{statusdata['weekly_goal']} ランキング: {statusdata['ranking']}",
                details=f"マイページ",
                buttons=[{"label": "WordEngineを実施する", "url": url}],
                instance=True
            )
        elif statusdata['status'] == "studyreport":
            url = "https://www.wordengine.jp/my_page.html"
            RPC.update(
                state=f"今日: {statusdata['daily_progress']}/{statusdata['daily_goal']} 今週: {statusdata['weekly_progress']}/{statusdata['weekly_goal']} ランキング: {statusdata['ranking']}",
                details=f"スタディーレポート",
                buttons=[{"label": "WordEngineを実施する", "url": url}],
                instance=True
            )
        elif statusdata['status'] == "flashwords":
            url = "https://www.wordengine.jp/my_page.html"
            RPC.update(
                state=f"実施中 {statusdata['progress']}/15",
                details=f"フラッシュワード",
                buttons=[{"label": "WordEngineを実施する", "url": url}],
                instance=True
            )
        elif statusdata['status'] == "wordpanic":
            url = "https://www.wordengine.jp/my_page.html"
            RPC.update(
                state=f"実施中...",
                details=f"ワードパニック",
                buttons=[{"label": "WordEngineを実施する", "url": url}],
                instance=True
            )
        else:
            RPC.update(
                state=f"ERROR",
                details=f"WordEngine",
                buttons=[{"label": "WordEngineを実施する", "url": url}],
                instance=True
            )
    beforestatusdata = statusdata
    time.sleep(1)

