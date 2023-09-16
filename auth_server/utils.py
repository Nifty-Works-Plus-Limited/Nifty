import json
import os
import requests
from users.models import User
from rest_framework.authentication import get_authorization_header
from oauth2_provider.models import AccessToken, RefreshToken
from dotenv import load_dotenv

load_dotenv()

CLIENT_CREDENTIAL = os.getenv('CLIENT_CREDENTIAL')


def get_user_from_request(request):
    auth_header = get_authorization_header(request).split()

    if auth_header and len(auth_header) == 2:
        tokenFromHeader = auth_header[1].decode('utf-8')
        token = AccessToken.objects.filter(token=tokenFromHeader).first()
        user = User.objects.filter(id=token.user_id).first()
        return user
    return 0


def create_oauth2_acess_token_object_from_request(request):
    username = request.data['email']
    password = request.data['password']

    url = "http://{host}/api/v1/nifty-auth/o/token/".format(
        host=request.get_host())
    authHeader = 'Basic {client_credential}'.format(
        client_credential=CLIENT_CREDENTIAL)
    postHeaders = {
        'Content-Type': 'application/x-www-form-urlencoded',
        'Authorization': authHeader
    }

    body = {
        'username': username,
        'password': password,
        'grant_type': 'password',
        'scope': 'read write'
    }
    result = requests.post(url, data=body, headers=postHeaders)

    return json.loads(result.content)
