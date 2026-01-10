from urllib.parse import parse_qs
from rest_framework_simplejwt.tokens import UntypedToken
from django.contrib.auth.models import AnonymousUser
from channels.middleware import BaseMiddleware
from channels.db import database_sync_to_async
from django.contrib.auth import get_user_model
from rest_framework_simplejwt.exceptions import InvalidToken, TokenError
from rest_framework_simplejwt.authentication import JWTAuthentication

User = get_user_model()

@database_sync_to_async
def get_user(token):
    try:
        valid_data = JWTAuthentication().get_validated_token(token)
        user = JWTAuthentication().get_user(valid_data)
        return user
    except (InvalidToken, TokenError, User.DoesNotExist):
        return AnonymousUser()

class JWTAuthMiddleware(BaseMiddleware):
    async def __call__(self, scope, receive, send):
        query_string = scope['query_string'].decode()
        query_params = parse_qs(query_string)
        token = query_params.get('token', [None])[0]

        scope['user'] = await get_user(token)
        return await super().__call__(scope, receive, send)
