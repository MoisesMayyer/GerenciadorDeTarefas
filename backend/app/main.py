from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware

from slowapi.middleware import SlowAPIMiddleware
from slowapi.errors import RateLimitExceeded
from slowapi import _rate_limit_exceeded_handler

from app.config import settings
from app.limiter import limiter
from app.routers.auth import router_auth
from app.routers.tarefas import rota_tarefas
from app.routers.usuarios import router_usuarios

app = FastAPI()
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)
app.add_middleware(SlowAPIMiddleware)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=False,
    allow_methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"],
    allow_headers=["Authorization", "Content-Type"],
)

app.include_router(rota_tarefas)
app.include_router(router_auth)
app.include_router(router_usuarios)

@app.get("/")
@limiter.limit("5/minutes")
async def root(request: Request):
    return {"message": "teste"}
