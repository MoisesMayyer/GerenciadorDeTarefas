from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.database.database import db, Base
from app.routers.auth import router_auth
from app.routers.tarefas import rota_tarefas
from app.routers.usuarios import router_usuarios

app = FastAPI()

# A API só aceita chamadas do frontend publicado no GitHub Pages.
# Para rodar o frontend localmente, adicione as origens locais em CORS_ORIGINS
# no backend/.env (ex.: http://localhost:5500).
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

Base.metadata.create_all(bind=db)


@app.get("/")
async def root():
    return {"message": "teste"}
