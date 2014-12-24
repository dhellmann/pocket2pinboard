#!/usr/bin/env python

# http://getpocket.com/developer/docs/authentication

from __future__ import print_function

from BaseHTTPServer import BaseHTTPRequestHandler, HTTPServer
import logging
import sys
import threading
import webbrowser

import requests


class AuthResponseHandler(BaseHTTPRequestHandler):

    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write('''
        <html><head><title>pocket2pinboard</title></head>
        <body>
        <h1>pocket2pinboard</h1>
        <p>You may close this window now.</p>
        <script>
        function closeMe() {
            window.close();
        }
        window.onload = closeMe;
        </script></body>
        ''')
        self.server.responded.set()
        return

    def log_request(self, code, size=0):
        # Do not log requests
        return


def start_auth_server():
    server = HTTPServer(('127.0.0.1', 0), AuthResponseHandler)
    ip, port = server.server_address
    url = 'http://%s:%s' % (ip, port)
    responded = threading.Event()
    server.responded = responded
    t = threading.Thread(name='auth-response-server',
                         target=server.serve_forever,
                         )
    t.setDaemon(True)
    t.start()


    def _wait_for_auth_response():
        print('Waiting for auth response')
        responded.wait()
        server.shutdown()

    return (url, _wait_for_auth_response)


# Start the HTTP server in a separate thread here so it is running
# when we ask for the request token. If the user has already logged in
# and permitted access to the app the redirect is called right away
# when the browser opens the auth_url.
redirect_url, waiter = start_auth_server()

consumer_key = '36063-85bfb816cc2d4a114623428e'

# Get the request code.
headers = {
    'X-Accept': 'application/json',
}
payload = {
    'consumer_key': consumer_key,
    'redirect_uri': redirect_url,
}
request_token_url = 'https://getpocket.com/v3/oauth/request'
response = requests.post(request_token_url, data=payload, headers=headers)
request_code = response.json()['code']

# Ask the user for permission for the app to access their account.
auth_url = 'https://getpocket.com/auth/authorize?request_token='\
           '%s&redirect_uri=%s' % (request_code, redirect_url)
webbrowser.open(auth_url)

# Wait for the redirect URL to be accessed in the browser.
waiter()

# Check if we were given permission to access the account.
authorize_url = 'https://getpocket.com/v3/oauth/authorize'
payload = {
    'consumer_key': consumer_key,
    'code': request_code,
}
response = requests.post(authorize_url, data=payload, headers=headers)
print(response.status_code)
print(response.text)

# response.status_code == 200 if authorization was allowed
# response.status_code == 403 if authorization was not allowed
