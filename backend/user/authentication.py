import jwt
import requests
from django.conf import settings
from django.contrib.auth import get_user_model
from my_exceptions import DataNotExist
from rest_framework import exceptions
from rest_framework.authentication import BaseAuthentication


class SafeJWTAuthentication(BaseAuthentication):

    def authenticate(self, request):

        User = get_user_model()
        authorization_header = request.headers.get("Authorization")

        if not authorization_header:
            raise exceptions.AuthenticationFailed("Token not provided")
        try:
            access_token = authorization_header.split(" ")[1]
            payload = requests.get(
                "https://www.googleapis.com/oauth2/v3/userinfo",
                "GET",
                headers={"Authorization": f"Bearer {access_token}"},
            )

        except jwt.ExpiredSignatureError:
            raise exceptions.AuthenticationFailed("access_token expired")

        except IndexError:
            raise exceptions.AuthenticationFailed("Token prefix missing")

        except Exception as e:
            raise exceptions.AuthenticationFailed(e.__str__())
        try:
            user = User.objects.get(email=payload.json()["email"])
        except Exception as e:
            raise DataNotExist(e.__str__())

        if user is None:
            raise exceptions.AuthenticationFailed("User not found")

        if user.is_deleted:
            raise exceptions.AuthenticationFailed("user is inactive")

        return user, None


def generate_access_token(user):
    return jwt.encode(
        {"email": user.email},
        settings.SECRET_KEY,
        algorithm="HS256",
    )
    

def generate_refresh_token(user):
    return jwt.encode(
        {"email": user.email},
        settings.SECRET_KEY,
        algorithm="HS256",
    )