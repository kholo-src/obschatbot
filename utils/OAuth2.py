import requests
import socket
import time
import webbrowser

BUFFER_SIZE = 2048
ENCODING = "utf-8"

HTML_RESPONSE = """
<!doctype>
<html>
<head>
    <title>Authorization granted</title>
    <script>window.close();</script>
</head>
<body>
<h1>Authorization granted</h1>
<p>You can close this window.</p>
</body>
</html>
"""

REDIRECT_HOST = "localhost"
REDIRECT_PORT = 8000
REDIRECT_URI = f"http://{REDIRECT_HOST}:{str(REDIRECT_PORT)}"

class OAuth2:

    code_url = ""
    authorization_url = ""
    refresh_url = ""
    client_id = ""
    client_secret = ""
    scope = ""
    access_token = ""
    refresh_token = ""
    grant_type = ""
    expiration_date = 0

    def set_credentials(self, client_id, client_secret):
        self.client_id = client_id
        self.client_secret = client_secret

    def set_refresh_token(self, refresh_token):
        self.refresh_token = refresh_token

    def get_authorization(self):
        params = {
            "client_id": self.client_id,
            "redirect_uri": REDIRECT_URI,
            "response_type": "code",
            "scope": self.scope.replace(" ", "%20")
        }
        url = f"{self.code_url}?{'&'.join([f'{key}={value}' for key, value in params.items()])}"
        webbrowser.open(url, 2)
        response = self.wait_for_code()
        return self.authorize(response["code"])

    def wait_for_code(self):
        httpd = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        httpd.bind((REDIRECT_HOST, REDIRECT_PORT))
        httpd.listen()
        waiting = True
        while waiting:
            client, addr = httpd.accept()
            response = client.recv(BUFFER_SIZE).decode(ENCODING)
            if "GET" in response and "code=" in response:
                client.send(bytes("HTTP/1.0 200 OK\n", ENCODING))
                client.send(bytes("Content-Type: text/html\n", ENCODING))
                client.send(bytes("\n", ENCODING))
                client.send(bytes(HTML_RESPONSE, ENCODING))
                client.close()
                waiting = False
        httpd.close()
        return self.parse_code_response(response)

    def parse_code_response(self, response_str):
        response = {}
        for param in response_str.split("\n")[0].split()[1][2:].split("&"):
            name, value = param.split("=")
            response[name] = value
        return response

    def authorize(self, code):
        response = requests.post(
            self.authorization_url,
            data={
                "grant_type": "authorization_code",
                "code": code,
                "redirect_uri": REDIRECT_URI
            },
            headers={"Authorization": f"Basic {self.get_client_headers()}"}
        )
        if not response.ok:
            return
        self.access_token = response.json()["access_token"]
        self.refresh_token = response.json()["refresh_token"]
        self.token_type = response.json()["token_type"]
        self.expiration_date = time.time() + response.json()["expires_in"]
        return self.refresh_token

    def refresh(self):
        response = requests.post(
            self.refresh_url,
            data={
                "grant_type": "refresh_token",
                "refresh_token": self.refresh_token
            },
            headers={"Authorization": f"Basic {self.get_client_headers()}"}
        )
        if not response.ok:
            return
        self.access_token = response.json()["access_token"]
        self.token_type = response.json()["token_type"]
        self.expiration_date = time.time() + response.json()["expires_in"]

    def get_client_headers(self):
        pass

    def has_expired(self):
        return time.time() > self.expiration_date
