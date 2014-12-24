# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or
# implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import BaseHTTPServer
import logging
import threading
import urllib
import webbrowser

import requests


LOG = logging.getLogger(__name__)


class AuthError(Exception):
    def __init__(self, status_code, error_msg):
        super(AuthError, self).__init__('Authentication failed: %s: %s'
                                        % (status_code, error_msg))
        self.status_code = status_code
        self.error_msg = error_msg


class AuthResponseHandler(BaseHTTPServer.BaseHTTPRequestHandler):

    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write('''
        <html><head><title>pocket2pinboard</title></head>
        <body>
        <h1>pocket2pinboard</h1>
        <p>You may close this window now.</p>
        <script type="text/javascript">
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


def _start_auth_server():
    server = BaseHTTPServer.HTTPServer(('127.0.0.1', 0),
                                       AuthResponseHandler)
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
        LOG.info('waiting for application authentication')
        responded.wait()
        server.shutdown()

    return (url, _wait_for_auth_response)


def authenticate(consumer_key):
    # Start the HTTP server in a separate thread here so it is running
    # when we ask for the request token. If the user has already logged in
    # and permitted access to the app the redirect is called right away
    # when the browser opens the auth_url.
    redirect_url, waiter = _start_auth_server()

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
    auth_url_base = 'https://getpocket.com/auth/authorize'
    auth_url_params = urllib.urlencode({
        'request_token': request_code,
        'redirect_uri': redirect_url,
    })
    auth_url = auth_url_base + '?' + auth_url_params
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
    if response.status_code == 200:
        return response.json()['access_token']
    raise AuthError(response.status_code, response.text)
