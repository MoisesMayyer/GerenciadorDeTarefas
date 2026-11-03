"""Testes de /auth.

POST /auth/login
  - 200 com access_token e token_type="bearer" usando form-urlencoded
    (não JSON).
  - 401 para senha incorreta.
  - 401 para e-mail inexistente.
  - 401 para usuário com ativo=False.

GET /auth/me
  - 200 devolvendo o usuário do token, sem expor o hash da senha.
  - 401 sem header Authorization.
  - 401 com token de assinatura inválida.
  - 401 com token expirado (montar token com exp no passado).
  - 401 com token sem "sub".
  - 401 com "sub" não numérico.
  - 401 com token de usuário inativo.
"""

from datetime import datetime, timedelta, timezone

import jwt

from app.config import settings
from app.database.models import Usuario


def criar_token(payload):
    return jwt.encode(payload, settings.SECRET_KEY, algorithm=settings.ALGORITHM)


def test_login_devolve_token(client, criar_usuario):
    criar_usuario(nome="ana", email="example@gmail.com", senha="senha123456789")

    resposta = client.post(
        "/auth/login",
        data={"username": "example@gmail.com", "password": "senha123456789"}
    )

    assert resposta.status_code == 200, resposta.text

    corpo = resposta.json()
    assert corpo["token_type"] == "bearer"
    assert corpo["access_token"]


def test_login_senha_invalida(client, criar_usuario):
    criar_usuario(nome="ana", email="example@gmail.com", senha="senha123456789")

    resposta = client.post(
        "/auth/login",
        data={"username": "example@gmail.com", "password": "senha_errada"}
    )

    assert resposta.status_code == 401, resposta.text


def test_login_email_invalido(client, criar_usuario):
    criar_usuario(nome="ana", email="ana@example.com", senha="senha123")

    resposta = client.post(
        "/auth/login",
        data={"username": "emailerrado@example.com", "password": "senha123"}
    )

    assert resposta.status_code == 401, resposta.text


def test_login_usuario_desativado(client, criar_usuario, db_session):
    usuario = criar_usuario(nome="ana")

    registro = db_session.get(Usuario, usuario["id"])
    registro.ativo = False

    db_session.commit()

    resposta = client.post(
        "/auth/login",
        data={"username": "ana@email.com", "password": "senha123"}
    )

    assert resposta.status_code == 401, resposta.text


def test_me_devolve_usuario_sem_hash(client, usuario, headers):
    resposta = client.get("/auth/me", headers=headers)

    assert resposta.status_code == 200, resposta.text
    corpo = resposta.json()

    assert corpo["id"] == usuario["id"]
    assert corpo["email"] == usuario["email"]
    assert corpo["nome"] == usuario["nome"]
    assert corpo["ativo"] is True
    assert "senha" not in corpo


def test_me_sem_token_retorna_401(client):
    resposta = client.get("/auth/me")

    assert resposta.status_code == 401, resposta.text


def test_me_token_assinatura_invalida_retorna_401(client):
    token = jwt.encode(
        {"sub": "1", "exp": datetime.now(timezone.utc) + timedelta(minutes=5)},
        "chave-errada-com-mais-de-32-caracteres",
        algorithm=settings.ALGORITHM,
    )

    resposta = client.get(
        "/auth/me",
        headers={"Authorization": f"Bearer {token}"}
    )

    assert resposta.status_code == 401, resposta.text


def test_me_token_expirado_retorna_401(client, usuario):
    token = criar_token({
        "sub": str(usuario["id"]),
        "exp": datetime.now(timezone.utc) - timedelta(minutes=1),
    })

    resposta = client.get(
        "/auth/me",
        headers={"Authorization": f"Bearer {token}"}
    )

    assert resposta.status_code == 401, resposta.text


def test_me_token_sem_sub_retorna_401(client):
    token = criar_token({
        "exp": datetime.now(timezone.utc) + timedelta(minutes=5),
    })

    resposta = client.get(
        "/auth/me",
        headers={"Authorization": f"Bearer {token}"}
    )

    assert resposta.status_code == 401, resposta.text


def test_me_token_sub_invalido_retorna_401(client):
    token = criar_token({
        "sub": "abc",
        "exp": datetime.now(timezone.utc) + timedelta(minutes=5),
    })

    resposta = client.get(
        "/auth/me",
        headers={"Authorization": f"Bearer {token}"}
    )

    assert resposta.status_code == 401, resposta.text


def test_me_usuario_inativo_retorna_401(
    client, usuario, headers, db_session
):
    registro = db_session.get(Usuario, usuario["id"])
    registro.ativo = False
    db_session.commit()

    resposta = client.get("/auth/me", headers=headers)

    assert resposta.status_code == 401, resposta.text

