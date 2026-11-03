import os
from pathlib import Path

import pytest
from dotenv import dotenv_values
from fastapi.testclient import TestClient
from sqlalchemy.engine import make_url

BACKEND_DIR = Path(__file__).resolve().parent.parent
_env = dotenv_values(BACKEND_DIR / ".env")

if not _env.get("DATABASE_URL"):
    raise RuntimeError("Defina DATABASE_URL em backend/.env")


TEST_DATABASE_URL = os.getenv("TEST_DATABASE_URL") or make_url(
    _env["DATABASE_URL"]
).set(database="test_gerenciador_tarefas").render_as_string(hide_password=False)

_banco = make_url(TEST_DATABASE_URL).database or ""
if not _banco.startswith("test_"):
    raise RuntimeError(
        f"Os testes só podem rodar em um banco iniciado por 'test_' (recebido: {_banco!r})."
    )


os.environ["DATABASE_URL"] = TEST_DATABASE_URL
os.environ.pop("TEST_DATABASE_URL", None)
os.environ["SECRET_KEY"] = "chave-secreta-apenas-para-testes"
os.environ["ALGORITHM"] = "HS256"
os.environ["ACCESS_TOKEN_EXPIRE_MINUTES"] = "30"
os.environ["CORS_ORIGINS"] = "http://localhost:5500"

from app.database.database import Base, SessionLocal, db as engine  # noqa: E402
from app.main import app  # noqa: E402


@pytest.fixture(autouse=True)
def banco_limpo():
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    yield


@pytest.fixture
def client():
    with TestClient(app) as cliente:
        yield cliente


@pytest.fixture
def db_session():
    sessao = SessionLocal()
    try:
        yield sessao
    finally:
        sessao.close()


@pytest.fixture
def criar_usuario(client):
    def _criar(nome="Ana", email="ana@email.com", senha="senha123", ativo= True):
        resposta = client.post(
            "/usuarios/",
            json={"nome": nome, "email": email, "senha": senha, "ativo": ativo},
        )
        assert resposta.status_code == 201, resposta.text
        return resposta.json()

    return _criar


@pytest.fixture
def autenticar(client):
    def _autenticar(email="ana@email.com", senha="senha123"):
        resposta = client.post(
            "/auth/login",
            data={"username": email, "password": senha},
        )
        assert resposta.status_code == 200, resposta.text
        token = resposta.json()["access_token"]
        return {"Authorization": f"Bearer {token}"}

    return _autenticar


@pytest.fixture
def usuario(criar_usuario):
    return criar_usuario()


@pytest.fixture
def headers(usuario, autenticar):
    return autenticar(email=usuario["email"])
