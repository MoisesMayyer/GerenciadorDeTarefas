import os
from pathlib import Path

# Pasta `backend/` (o conftest.py está em backend/tests/).
BACKEND_DIR = Path(__file__).resolve().parent.parent

# Banco SQLite usado só pelos testes. O *.db está no .gitignore.
BANCO_DE_TESTE = BACKEND_DIR / "test.db"

os.environ["SECRET_KEY"] = "chave-secreta-apenas-para-testes"
os.environ["ALGORITHM"] = "HS256"
os.environ["ACCESS_TOKEN_EXPIRE_MINUTES"] = "30"
os.environ["DATABASE_URL"] = f"sqlite:///{BANCO_DE_TESTE}"
os.environ["CORS_ORIGINS"] = "http://localhost:5500"

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import sessionmaker

from app.database.database import Base, db as engine
from app.main import app


@pytest.fixture(scope="session", autouse=True)
def banco_temporario():

    Base.metadata.create_all(bind=engine)
    yield
    engine.dispose()
    BANCO_DE_TESTE.unlink(missing_ok=True)


@pytest.fixture(autouse=True)
def banco_limpo():

    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    yield


@pytest.fixture
def db_session():

    session = sessionmaker(bind=engine)
    sessao = session()
    try:
        yield sessao
    finally:
        sessao.close()


@pytest.fixture
def client():

    return TestClient(app)

@pytest.fixture
def criar_usuario(client):

    def _criar_usuario(nome="Ana", email="ana@email.com", senha="senha123"):
        resposta = client.post(
            "/usuarios/",
            json={"nome": nome, "email": email, "senha": senha},
        )
        # Se falhar aqui, o problema é no teste.
        assert resposta.status_code == 201, resposta.text
        return resposta.json()

    return _criar_usuario


@pytest.fixture
def autenticar(client):

    def _autenticar(email="ana@email.com", senha="senha123"):
        resposta = client.post(
            "/auth/login",
            data={"username": email, "password": senha},  # form, não JSON
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


@pytest.fixture
def criar_tarefa(client):

    def _criar_tarefa(
        headers,
        nome="Estudar FastAPI",
        descricao="rotas, schemas e testes",
        status=None,
    ):
        corpo = {"nome": nome, "descricao": descricao}
        if status is not None:
            corpo["status"] = status

        resposta = client.post("/tarefas/nova_tarefa", json=corpo, headers=headers)
        assert resposta.status_code == 201, resposta.text
        return resposta.json()

    return _criar_tarefa
