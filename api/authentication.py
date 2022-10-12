from rest_framework import status, exceptions
from django.http import HttpResponse
from rest_framework.authentication import TokenAuthentication
from rest_framework.authentication import get_authorization_header, BaseAuthentication
import jwt
import json
from django.conf import settings
from rest_framework.response import Response
from .models import User

class MyOwnTokenAuthentication(TokenAuthentication):

    def authenticate(self, request):
        auth = get_authorization_header(request).split()
        if not auth or auth[0].lower() != b'bearer':
            return None

        if len(auth) == 1:
            msg = 'Invalid token header. No credentials provided.'
            raise exceptions.AuthenticationFailed(msg)
        elif len(auth) > 2:
            msg = 'Invalid token header'
            raise exceptions.AuthenticationFailed(msg)

        try:
            token = auth[1]
            if token=="null":
                msg = 'Null token not allowed'
                raise exceptions.AuthenticationFailed(msg)
        except UnicodeError:
            msg = 'Invalid token header. Token string should not contain invalid characters.'
            raise exceptions.AuthenticationFailed(msg)

        return self.authenticate_credentials(token)

    def authenticate_credentials(self, token):
        try:
            payload = jwt.decode(token, settings.SECRET_KEY, algorithms="HS256")

            email = payload['email']
            
            try: 
                user = User.objects.get(email=email)
            except User.DoesNotExist:
                msg = {"detail": "User Not Found"}
                raise exceptions.AuthenticationFailed(msg)

        except jwt.ExpiredSignatureError:            
            msg = {"detail": "Token Expired"}
            raise exceptions.AuthenticationFailed(msg)

        except (jwt.InvalidTokenError,jwt.DecodeError):  
            msg = {"detail": "Token is invalid"}
            raise exceptions.AuthenticationFailed(msg)

        return (user, token)

