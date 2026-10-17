from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.database.database import db, Base
from app.routers.tarefas import rota_tarefas

app = FastAPI()

# Libera o acesso do frontend (que roda em outra porta/host) à API
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(rota_tarefas)


Base.metadata.create_all(bind=db)


@app.get("/")
async def root():
    return {"message": "teste"}
