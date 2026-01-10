from urllib.parse import parse_qs
from channels.middleware.base import BaseMiddleware
from channels.db import database_sync_to_async
from django.contrib.auth.models import AnonymousUser
from django.contrib.auth import get_user_model
from rest_framework_simplejwt.tokens import UntypedToken
from rest_framework_simplejwt.exceptions import InvalidToken, TokenError
from rest_framework_simplejwt.backends import TokenBackend
from django.conf import settings

@database_sync_to_async
def get_user(validated_token):
    User = get_user_model()
    try:
        user_id = validated_token[settings.SIMPLE_JWT['USER_ID_CLAIM']]
        return User.objects.get(id=user_id)
    except User.DoesNotExist:
        return AnonymousUser()

class JWTAuthMiddleware(BaseMiddleware):
    async def __call__(self, scope, receive, send):
        query_string = parse_qs(scope["query_string"].decode())
        token = query_string.get("token", [None])[0]

        if token is None:
            scope["user"] = AnonymousUser()
            return await super().__call__(scope, receive, send)

        try:
            validated_token = TokenBackend(algorithm='HS256').decode(token, verify=True)
            scope["user"] = await get_user(validated_token)
        except (InvalidToken, TokenError) as e:
            scope["user"] = AnonymousUser()

        return await super().__call__(scope, receive, send)
