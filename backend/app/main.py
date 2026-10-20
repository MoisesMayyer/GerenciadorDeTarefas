from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.database.database import db, Base
from app.routers.auth import router_auth
from app.routers.tarefas import rota_tarefas
from app.routers.usuarios import router_usuarios

app = FastAPI()

# Libera o acesso do frontend (que roda em outra porta/host) à API
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(rota_tarefas)
app.include_router(router_auth)
app.include_router(router_usuarios)

Base.metadata.create_all(bind=db)


@app.get("/")
async def root():
    return {"message": "teste"}
