"""Testes de /usuarios.

POST /usuarios/
  - 201 criando conta e devolvendo id, nome, email, ativo (sem senha).
  - 409 para e-mail já cadastrado.
  - 422 para nome vazio/curto, e-mail inválido, senha < 6 ou > 128.
  - E-mail salvo em minúsculas.

GET /usuarios/
  - 200 devolvendo apenas a própria conta, mesmo com outras no banco.

GET /usuarios/{id}
  - 200 para o próprio id.
  - 404 para id de outra conta.
  - 401 sem token.

PUT /usuarios/{id}
  - 200 atualizando só os campos enviados.
  - 200 ao trocar a senha e o login funcionar com a nova.
  - 409 ao tentar e-mail de outra conta.
  - 404 para id de outra conta.

PATCH /usuarios/{id}/cancelar
  - 200 com ativo=False.
  - Token do usuário deixa de autenticar (401) após o cancelamento.
  - 404 para id de outra conta.

DELETE /usuarios/{id}
  - 204 e o usuário não autentica mais.
  - 404 para id de outra conta.
  - Exclusão em cascata: as tarefas do usuário somem do banco.
"""

import pytest

from app.database.models import Tarefa

#post - test
def test_criar_usuario(client):
    resposta = client.post(
        "/usuarios/",
        json={
            "nome": "teste",
            "email": "email@example.com",
            "senha": "senhaforte123",
        }
    )

    assert resposta.status_code == 201, resposta.text
    corpo = resposta.json()

    assert corpo["id"]
    assert corpo["nome"] == "teste"
    assert corpo["email"] == "email@example.com"
    assert corpo["ativo"] is True
    assert "senha" not in corpo


@pytest.mark.parametrize(
    "nome, email, senha",
    [
        ("ana", "email@example.com", "senha"),  # senha curta
        ("", "email@example.com", "senhaforte123"),  # nome vazio
        ("a" * 51, "email@example.com", "senhaforte123"),  # nome longo
        ("ana", "emailinvalido.com", "senhaforte123"),  # e-mail inválido
        ("ana", "email@example.com", "a" * 129),  # senha longa
    ]
)
def test_criar_usuario_invalido(client, nome, email, senha):
    resposta = client.post(
        "/usuarios/",
        json={"nome": nome, "email": email, "senha": senha}
    )

    assert resposta.status_code == 422, resposta.text


def test_criar_usuario_email_duplicado(client):
    email = "emailrepetido@example.com"

    client.post(
        "/usuarios/",
        json={"nome": "ana", "email": email, "senha": "senhaforte123"}
    )


    resposta = client.post(
        "/usuarios/",
        json={"nome": "jose", "email": email, "senha": "senhaforte123"}
    )

    assert resposta.status_code == 409, resposta.text
    assert resposta.json()["detail"] == "email ja cadastrado"


def test_criar_usuario_email_minusculo(client):
    resposta = client.post(
        "/usuarios/",
        json={
            "nome": "ana",
            "email": "ANA@EXAMPLE.COM",
            "senha": "senhaforte123",
        }
    )

    assert resposta.status_code == 201, resposta.text

    assert resposta.json()["email"] == "ana@example.com"


#get - test
def test_listar_apenas_proprio_usuario(client, usuario, headers, criar_usuario):
    criar_usuario(nome="Bia", email="bia@example.com", senha="senhaforte123")

    resposta = client.get("/usuarios/", headers=headers)

    assert resposta.status_code == 200, resposta.text
    corpo = resposta.json()

    assert len(corpo) == 1
    assert corpo[0]["id"] == usuario["id"]


def test_buscar_proprio_usuario_por_id(client, usuario, headers):
    resposta = client.get(f"/usuarios/{usuario['id']}", headers=headers)

    assert resposta.status_code == 200, resposta.text
    corpo = resposta.json()

    assert corpo["id"] == usuario["id"]
    assert corpo["email"] == usuario["email"]
    assert "senha" not in corpo


def test_buscar_usuario_de_outra_conta_retorna_404(client, headers, criar_usuario):
    outro = criar_usuario(nome="Bia", email="bia@example.com", senha="senhaforte123")

    resposta = client.get(f"/usuarios/{outro['id']}", headers=headers)

    assert resposta.status_code == 404, resposta.text


def test_buscar_usuario_sem_token_retorna_401(client, usuario):
    resposta = client.get(f"/usuarios/{usuario['id']}")

    assert resposta.status_code == 401, resposta.text


#put - test
def test_atualizar_usuario_parcial(client, usuario, headers):
    # Envia só o nome, sem e-mail e sem senha.
    resposta = client.put(
        f"/usuarios/{usuario['id']}",
        headers=headers,
        json={"nome": "Ana Maria"}
    )

    assert resposta.status_code == 200, resposta.text
    corpo = resposta.json()

    assert corpo["nome"] == "Ana Maria"
    assert corpo["email"] == usuario["email"]
    assert "senha" not in corpo


def test_atualizar_senha_e_logar_com_nova(client, usuario, headers):
    # Troca a senha da conta.
    resposta = client.put(
        f"/usuarios/{usuario['id']}",
        headers=headers,
        json={"senha": "novaSenha123"}
    )

    assert resposta.status_code == 200, resposta.text

    resposta = client.post(
        "/auth/login",
        data={"username": usuario["email"], "password": "senha123"}
    )

    assert resposta.status_code == 401, resposta.text

    resposta = client.post(
        "/auth/login",
        data={"username": usuario["email"], "password": "novaSenha123"}
    )

    assert resposta.status_code == 200, resposta.text
    assert resposta.json()["access_token"]


def test_atualizar_usuario_com_email_de_outra_conta_retorna_409(
    client, usuario, headers, criar_usuario
):
    # Cria uma segunda conta.
    outro = criar_usuario(nome="Bia", email="bia@example.com", senha="senhaforte123")

    # Tenta usar o e-mail da outra conta.
    resposta = client.put(
        f"/usuarios/{usuario['id']}",
        headers=headers,
        json={"email": outro["email"]}
    )

    assert resposta.status_code == 409, resposta.text
    assert resposta.json()["detail"] == "email ja cadastrado"


def test_atualizar_usuario_de_outra_conta_retorna_404(client, headers, criar_usuario):
    outro = criar_usuario(nome="Bia", email="bia@example.com", senha="senhaforte123")

    resposta = client.put(
        f"/usuarios/{outro['id']}",
        headers=headers,
        json={"nome": "Bia Maria"}
    )

    assert resposta.status_code == 404, resposta.text


#patch - test
def test_cancelar_usuario(client, usuario, headers):
    resposta = client.patch(
        f"/usuarios/{usuario['id']}/cancelar",
        headers=headers
    )

    assert resposta.status_code == 200, resposta.text
    assert resposta.json()["ativo"] is False


def test_token_de_usuario_cancelado_retorna_401(client, usuario, headers):
    resposta = client.patch(
        f"/usuarios/{usuario['id']}/cancelar",
        headers=headers
    )
    assert resposta.status_code == 200, resposta.text

    resposta = client.get("/usuarios/", headers=headers)

    assert resposta.status_code == 401, resposta.text


def test_cancelar_usuario_de_outra_conta_retorna_404(client, headers, criar_usuario):
    outro = criar_usuario(nome="Bia", email="bia@example.com", senha="senhaforte123")

    resposta = client.patch(
        f"/usuarios/{outro['id']}/cancelar",
        headers=headers
    )

    assert resposta.status_code == 404, resposta.text


#delete - test
def test_deletar_usuario(client, usuario, headers):
    resposta = client.delete(
        f"/usuarios/{usuario['id']}",
        headers=headers
    )

    assert resposta.status_code == 204, resposta.text
    assert resposta.content == b""

    resposta = client.get("/usuarios/", headers=headers)

    assert resposta.status_code == 401, resposta.text


def test_deletar_usuario_de_outra_conta_retorna_404(client, headers, criar_usuario):
    outro = criar_usuario(nome="Bia", email="bia@example.com", senha="senhaforte123")

    resposta = client.delete(
        f"/usuarios/{outro['id']}",
        headers=headers
    )

    assert resposta.status_code == 404, resposta.text


def test_deletar_usuario_remove_tarefas(client, usuario, headers, db_session):
    resposta = client.post(
        "/tarefas/nova_tarefa",
        headers=headers,
        json={"nome": "Tarefa da Ana", "descricao": ""}
    )
    assert resposta.status_code == 201, resposta.text

    resposta = client.delete(
        f"/usuarios/{usuario['id']}",
        headers=headers
    )
    assert resposta.status_code == 204, resposta.text

    total = db_session.query(Tarefa).filter(
        Tarefa.usuario_id == usuario["id"]
    ).count()

    assert total == 0

