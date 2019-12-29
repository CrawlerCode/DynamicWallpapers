import webbrowser, json, requests, time
from flask import Flask, request, redirect
from requests import auth
from pythontools.core import logger

class Spotify():

    def __init__(self):
        self.endpoint_code = ""
        self.access_token = ""
        self.expires_in = 0
        self.refresh_token = ""
        self.client_id = ""
        self.client_sequence = ""
        self.session = requests.Session()

    def setClientID(self, client_id):
        self.client_id = client_id

    def generateClientSequence(self, client_id, client_secret):
        return auth._basic_auth_str(client_id, client_secret)

    def setClientSequence(self, client_sequence):
        self.client_sequence = client_sequence

    def refreshToken(self):
        if self.refresh_token == "":
            logger.log("§8[§cERROR§8] No refresh token!")
            return
        response = self._post('https://accounts.spotify.com/api/token', data={'grant_type': 'refresh_token', 'refresh_token': self.refresh_token}, headers={'Authorization': self.client_sequence})
        if response.status_code == 200:
            response = json.loads(response.text)
            self.access_token = response["access_token"]
            self.expires_in = time.time() + response["expires_in"] - 60
            logger.log("§aSpotify token refreshed")
        else:
            logger.log("§8[§cERROR§8] Failed to refresh token: " + str(response.text))

    def getUserAccess(self, app_name):
        webbrowser.open('https://accounts.spotify.com/authorize?client_id=' + self.client_id + '&response_type=code&redirect_uri=http://127.0.0.1/&scope=user-read-currently-playing', new=0, autoraise=True)
        self.endpoint_code = ''
        app = Flask(app_name)
        @app.route("/", methods=["GET"])
        def index():
            if request.method == "GET" and "code" in request.args:
                self.endpoint_code = request.args["code"]
                request.environ.get('werkzeug.server.shutdown')()
                return redirect('https://www.spotify.com/de/')
            return "Failed: No code!"
        app.run(host="0.0.0.0", port=80, debug=False, threaded=False, use_reloader=False)
        response = json.loads(self._post('https://accounts.spotify.com/api/token', data={'grant_type': 'authorization_code', 'code': self.endpoint_code, 'redirect_uri': 'http://127.0.0.1/'}, headers={'Authorization': self.client_sequence}).text)
        if "error" in response:
            logger.log("§8[§cERROR§8] Failed to get User-Access: " + str(response))
            return
        self.access_token = response["access_token"]
        self.expires_in = time.time() + response["expires_in"] - 60
        self.refresh_token = response["refresh_token"]
        logger.log("§aUser-Access ok")

    def loadToken(self, access_token, expires_in, refresh_token):
        self.access_token = access_token
        self.expires_in = expires_in
        self.refresh_token = refresh_token

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

    def getCurrentPlaying(self):
        response = self._get_request_authenticated('https://api.spotify.com/v1/me/player/currently-playing')
        if response.status_code == 200:
            return json.loads(response.text)