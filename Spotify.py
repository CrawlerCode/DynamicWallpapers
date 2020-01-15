import webbrowser, requests, time
from flask import Flask, request, redirect
from requests import auth
from pythontools.core import logger, tools

class Spotify():

    def __init__(self):
        self.endpoint_code = ""
        self.access_token = ""
        self.expires_in = 0
        self.refresh_token = ""
        self.client_id = ""
        self.client_sequence = ""
        self.scope = ""
        self.session = requests.Session()

    def init(self, client_id, client_sequence, scope=""):
        self.setClientID(client_id=client_id)
        self.setClientSequence(client_sequence=client_sequence)
        self.loadToken()
        if not self.hasToken(scope=scope):
            self.getUserAccess(scope=scope)
            self.saveToken()

    def setClientID(self, client_id):
        self.client_id = client_id

    def getClientSequence(self, client_id, client_secret):
        return auth._basic_auth_str(client_id, client_secret)

    def setClientSequence(self, client_sequence):
        self.client_sequence = client_sequence

    def hasToken(self, scope):
        ok = True
        for s in scope.split(" "):
            if s not in self.scope.split(" "):
                ok = False
        return self.refresh_token != "" and ok is True

    def refreshToken(self):
        if self.refresh_token == "":
            logger.log("§8[§cERROR§8] No refresh token!")
            return
        response = self._post('https://accounts.spotify.com/api/token', data={'grant_type': 'refresh_token', 'refresh_token': self.refresh_token}, headers={'Authorization': self.client_sequence})
        if response.status_code == 200:
            response = response.json()
            self.access_token = response["access_token"]
            self.expires_in = time.time() + response["expires_in"] - 60
            logger.log("§aSpotify token refreshed")
        else:
            logger.log("§8[§cERROR§8] Failed to refresh token: " + str(response.text))

    def getUserAccess(self, scope=""):
        webbrowser.open('https://accounts.spotify.com/authorize?client_id=' + self.client_id + '&response_type=code&redirect_uri=http://127.0.0.1/&scope=' + scope, new=0, autoraise=True)
        self.endpoint_code = ''
        app = Flask("User-Access")
        @app.route("/", methods=["GET"])
        def index():
            if request.method == "GET" and "code" in request.args:
                self.endpoint_code = request.args["code"]
                request.environ.get('werkzeug.server.shutdown')()
                return redirect('https://www.spotify.com/de/')
            return "Failed: No code!"
        app.run(host="0.0.0.0", port=80, debug=False, threaded=False, use_reloader=False)
        response = self._post('https://accounts.spotify.com/api/token', data={'grant_type': 'authorization_code', 'code': self.endpoint_code, 'redirect_uri': 'http://127.0.0.1/'}, headers={'Authorization': self.client_sequence})
        response = response.json()
        if "error" in response:
            logger.log("§8[§cERROR§8] Failed to get User-Access: " + str(response))
            return False
        self.access_token = response["access_token"]
        self.expires_in = time.time() + response["expires_in"] - 60
        self.refresh_token = response["refresh_token"]
        self.scope = response["scope"]
        logger.log("§aUser-Access ok")
        return True

    def saveToken(self, path="token.json"):
        tools.saveJson(path, {"access_token": self.access_token, "expires_in": self.expires_in, "refresh_token": self.refresh_token, "scope": self.scope})

    def loadToken(self, path="token.json"):
        if tools.existFile(path):
            data = tools.loadJson("token.json")
            self.access_token = data["access_token"]
            self.expires_in = data["expires_in"]
            self.refresh_token = data["refresh_token"]
            self.scope = data["scope"]

    def setToken(self, access_token, expires_in, refresh_token, scope=""):
        self.access_token = access_token
        self.expires_in = expires_in
        self.refresh_token = refresh_token
        self.scope = scope

    def getToken(self):
        if time.time() >= self.expires_in:
            self.refreshToken()
        return self.access_token

    def _get(self, url, data={}, headers={}):
        return self.session.get(url, headers=headers, data=data)

    def _post(self, url, data={}, headers={}):
        return self.session.post(url, headers=headers, data=data)

    def _get_request_authenticated(self, url, data={}):
        return self._get(url, data, headers={'Authorization': 'Bearer ' + self.getToken(), 'Content-Type': 'application/json'})

    def _post_request_authenticated(self, url, data={}):
        return self._post(url, data, headers={'Authorization': 'Bearer ' + self.getToken(), 'Content-Type': 'application/json'})

    def getCurrentPlaying(self):
        response = self._get_request_authenticated('https://api.spotify.com/v1/me/player/currently-playing')
        if response.status_code == 200:
            return response.json()
        else:
            print(response.json())