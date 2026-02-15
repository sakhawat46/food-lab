from fastapi import FastAPI
from apps.fastapi_app.routes_profile import router as profile_router

fastapi_app = FastAPI()

fastapi_app.include_router(profile_router)

@fastapi_app.post("/sum")
def calculate_sum(data: dict):
    a = data.get("a", 0)
    b = data.get("b", 0)
    return {"result": a + b}

