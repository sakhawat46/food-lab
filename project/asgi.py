import os
from django.core.asgi import get_asgi_application
from starlette.applications import Starlette
from starlette.routing import Mount

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "project.settings")

django_asgi_app = get_asgi_application()

from apps.fastapi_app.app import fastapi_app

app = Starlette(routes=[
    Mount("/fast", app=fastapi_app),   # আগে FastAPI
    Mount("/", app=django_asgi_app),   # পরে Django (catch-all)
])