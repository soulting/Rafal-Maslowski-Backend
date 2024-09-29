import base64
import hashlib
import os
import secrets
import string
import requests
import json

from dotenv import load_dotenv

load_dotenv()

CLIENT_ID = "843f1ece4c5b406e898fe2db517c8f0b"  # wprowadź Client_ID aplikacji
CLIENT_SECRET = "qupea5XdQD76jYrqrbHJcyA8BiDf6tsDc9ShcB3fDLhDAwBFSr99GG5E10Ye2rqS"  # wprowadź Client_Secret aplikacji
REDIRECT_URI = "http://localhost:8000"  # wprowadź redirect_uri
AUTH_URL = "https://allegro.pl.allegrosandbox.pl/auth/oauth/authorize"
TOKEN_URL = "https://allegro.pl.allegrosandbox.pl/auth/oauth/token"


def generate_code_verifier():
    code_verifier = ''.join((secrets.choice(string.ascii_letters) for i in range(40)))
    return code_verifier


def generate_code_challenge(code_verifier):
    hashed = hashlib.sha256(code_verifier.encode('utf-8')).digest()
    base64_encoded = base64.urlsafe_b64encode(hashed).decode('utf-8')
    code_challenge = base64_encoded.replace('=', '')
    return code_challenge


def get_authorization_code(code_verifier):
    code_challenge = generate_code_challenge(code_verifier)
    authorization_redirect_url = f"{AUTH_URL}?response_type=code&client_id={CLIENT_ID}&redirect_uri={REDIRECT_URI}" \
                                 f"&code_challenge_method=S256&code_challenge={code_challenge}"
    print(
        "Zaloguj do Allegro - skorzystaj z url w swojej przeglądarce oraz wprowadź authorization code ze zwróconego url: ")
    print(f"--- {authorization_redirect_url} ---")
    authorization_code = input('code: ')
    return authorization_code


def get_access_token(authorization_code, code_verifier):
    try:
        data = {'grant_type': 'authorization_code', 'code': authorization_code,
                'redirect_uri': REDIRECT_URI, 'code_verifier': code_verifier}
        access_token_response = requests.post(TOKEN_URL, data=data, verify=False,
                                              allow_redirects=False)
        response_body = json.loads(access_token_response.text)
        return response_body
    except requests.exceptions.HTTPError as err:
        raise SystemExit(err)


def main():
    code_verifier = generate_code_verifier()
    authorization_code = get_authorization_code(code_verifier)
    response = get_access_token(authorization_code, code_verifier)
    access_token = response['access_token']
    print(f"access token = {access_token}")


def get_order_events(token):
    try:
        parameters = {
            "type": ["READY_FOR_PROCESSING"]
        }
        url = "https://api.allegro.pl.allegrosandbox.pl/order/events"
        headers = {'Authorization': 'Bearer ' + token, 'Accept': "application/vnd.allegro.public.v1+json"}
        order_events_result = requests.get(url, headers=headers, verify=False, params=parameters)
        return order_events_result
    except requests.exceptions.HTTPError as err:
        raise SystemExit(err)


if __name__ == "__main__":
    # main()
    response = get_order_events(os.getenv("TOKEN"))
    print(response.json())
