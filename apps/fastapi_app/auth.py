from fastapi import Depends, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

security = HTTPBearer()


def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    # Lazy imports (Django settings loaded না থাকলে crash করবে না)
    from django.contrib.auth import get_user_model
    from rest_framework_simplejwt.tokens import AccessToken
    from rest_framework_simplejwt.exceptions import TokenError

    User = get_user_model()
    token = credentials.credentials

    try:
        access_token = AccessToken(token)
        user_id = access_token.get("user_id")
        return User.objects.get(id=user_id, is_active=True)

    except User.DoesNotExist:
        raise HTTPException(status_code=401, detail="User not found")
    except TokenError:
        raise HTTPException(status_code=401, detail="Invalid or expired token")
    except Exception:
        raise HTTPException(status_code=401, detail="Authentication failed")