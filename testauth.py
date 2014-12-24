#!/usr/bin/env python

# http://getpocket.com/developer/docs/authentication

from __future__ import print_function

import threading
import webbrowser

import requests


consumer_key = '36063-85bfb816cc2d4a114623428e'

headers = {
    'X-Accept': 'application/json',
}

redirect_uri = 'http://127.0.0.1:8000'

payload = {
    'consumer_key': consumer_key,
    'redirect_uri': redirect_uri,
}
request_token_url = 'https://getpocket.com/v3/oauth/request'
response = requests.post(request_token_url, data=payload, headers=headers)

print(response.json())

request_code = response.json()['code']
print('request_code = %s' % request_code)

# Start the HTTP server in a separate thread here so it is running
# when we ask for the request token. If the user has already logged in
# and permitted access to the app the redirect is called right away
# when the browser opens the auth_url.

auth_url = 'https://getpocket.com/auth/authorize?request_token='\
           '%s&redirect_uri=%s' % (request_code, redirect_uri)
webbrowser.open(auth_url)

# Use a threading event set by the HTTP server and wait for that here
# instead of prompting for user input.
raw_input('press return to continue')

authorize_url = 'https://getpocket.com/v3/oauth/authorize'
payload = {
    'consumer_key': consumer_key,
    'code': request_code,
}
response = requests.post(authorize_url, data=payload, headers=headers)
print(response.text)

# response.status_code == 200 if authorization was allowed
# response.status_code == 403 if authorization was not allowed
