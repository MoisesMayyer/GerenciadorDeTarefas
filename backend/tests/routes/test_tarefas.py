"""Testes de /tarefas.

POST /tarefas/nova_tarefa
  - 201 com status "pendente" por padrão.
  - usuario_id vem do token e é ignorado se enviado no corpo.
  - 422 sem nome e com status fora do enum.

GET /tarefas/
  - 200 listando só as tarefas do dono.
  - 200 com lista vazia para usuário sem tarefas.
  - Tarefas com deletado=True NÃO aparecem.

GET /tarefas/tarefa/{id}
  - 200 para o dono.
  - 404 para tarefa de outro usuário.
  - 404 para id inexistente.
  - 404 para tarefa com deletado=True.

PUT /tarefas/atualizar_tarefa/{id}
  - 200 atualização parcial (só o campo enviado muda).
  - Campos null/omitidos não sobrescrevem.
  - 404 para tarefa de outro usuário.
  - 404 para tarefa deletada.
  - 422 com status inválido.

PATCH /tarefas/cancelar_tarefa/{id}
  - 200 e status vira "cancelado".
  - 404 para tarefa de outro usuário.
  - 404 para tarefa já deletada.

DELETE /tarefas/deletar_tarefa/{id}   (soft delete)
  - 204 e o corpo vem vazio.
  - PUT, PATCH e um segundo DELETE respondem 404.
  - A linha continua no banco com deletado=True
  - 404 para tarefa de outro usuário (não deleta nada).
"""
import pytest

from app.database.models import Tarefa


#post - test
def test_criar_tarefa_valida(client, headers):
    resposta = client.post(
        "/tarefas/nova_tarefa",
        json={
            "nome": "Tarefa válida de teste",
            "descricao": "Descrição da tarefa válida"
        },
        headers=headers)

    assert resposta.status_code == 201
    assert resposta.json()["status"] == "pendente"

    corpo = resposta.json()
    assert corpo["status"] == "pendente"
    assert "usuario_id" not in corpo


@pytest.mark.parametrize(
    "nome, descricao, status",
    [
        ("","teste","pendente"),
        ("teste","teste", "abacate"),
    ]
)
def test_criar_tarefa_invalida(client, headers, nome,descricao,status):
    resposta = client.post(
        "/tarefas/nova_tarefa",
        headers=headers,
        json={
            "nome": nome,
            "descricao": descricao,
            "status": status
        }
    )

    assert resposta.status_code == 422


#get - test
def test_listar_tarefa_dono(client,usuario,headers):
    criada =client.post(
        "/tarefas/nova_tarefa",
        headers=headers,
        json={
            "nome": "teste",
            "descricao": "teste",
            "status": "pendente"
        }

    )
    assert criada.status_code == 201

    tarefa = criada.json()

    resposta = client.get("/tarefas/", headers=headers)
    assert resposta.status_code == 200

    corpo = resposta.json()

    assert len(corpo) == 1

    assert corpo[0]["id"] == tarefa["id"]
    assert corpo[0]["nome"] == "teste"
    assert corpo[0]["descricao"] == "teste"
    assert corpo[0]["status"] == "pendente"


def test_listar_tarefas_vazias(client, headers):
    resposta = client.get(
        "/tarefas/",
        headers=headers
    )
    assert resposta.status_code == 200, resposta.text
    assert resposta.json() == []


def test_tarefa_deletada(client,headers):
    criada = client.post(
        "/tarefas/nova_tarefa",
        headers=headers,
        json={"nome": "tarefa da ana", "descricao": "privada"},
    )
    assert criada.status_code == 201, criada.text
    assert criada.json()["nome"] == "tarefa da ana"

    tarefa_id = criada.json()["id"]

    deletar_tarefa = client.delete(f"/tarefas/deletar_tarefa/{tarefa_id}", headers=headers)
    assert deletar_tarefa.status_code == 204, deletar_tarefa.text
    assert deletar_tarefa.content == b""

    resposta = client.get(
        "/tarefas/",
        headers=headers
    )
    assert resposta.json() == []


#get{id} - test
def test_listar_unica_tarefa(client,headers):
    criada = client.post(
        "/tarefas/nova_tarefa",
        headers=headers,
        json={"nome":"test", "descricao": "teste"}
    )
    assert criada.status_code == 201
    tarefa_id = criada.json()["id"]

    resposta = client.get(
        f"/tarefas/tarefa/{tarefa_id}",
        headers=headers
    )
    assert resposta.status_code == 200
    assert resposta.json()["nome"] == "test"


def test_tarefa_inexistente(client,headers):
    resposta = client.get(
        f"/tarefas/tarefa/{999999}",
        headers=headers
    )
    assert resposta.status_code == 404


def test_tarefa_id_invalido(client, headers):
    resposta = client.get(
        f"/tarefas/tarefa/{"abcjsdw"}",
        headers=headers
    )

    assert resposta.status_code == 422


def test_tarefa_deletada_404(client,headers):
    criado = client.post(
        "/tarefas/nova_tarefa",
        headers=headers,
        json={"nome": "teste", "descricao": "privada"},
    )
    assert criado.status_code == 201, criado.text
    assert criado.json()["nome"] == "teste"

    tarefa_id = criado.json()["id"]

    deletar_tarefa = client.delete(f"/tarefas/deletar_tarefa/{tarefa_id}", headers=headers)
    assert deletar_tarefa.status_code == 204, deletar_tarefa.text
    assert deletar_tarefa.content == b""

    resposta = client.get(
        f"/tarefas/tarefa/{tarefa_id}",
        headers=headers
    )
    assert resposta.status_code == 404
    assert resposta.json()["detail"] == "tarefa nao encontrada"


def test_listar_tarefa_outro_usuario(client, headers, criar_usuario, autenticar):
    criada = client.post(
        "/tarefas/nova_tarefa",
        headers=headers,
        json={"nome": "tarefa da ana", "descricao": "privada"},
    )
    assert criada.status_code == 201, criada.text
    tarefa_id = criada.json()["id"]

    criar_usuario(nome="jose", email="email2@example.com", senha="senha123")
    headers_jose = autenticar(email="email2@example.com")

    resposta = client.get("/tarefas/", headers=headers_jose)

    assert resposta.status_code == 200, resposta.text
    assert resposta.json() == []

    resposta = client.get(f"/tarefas/tarefa/{tarefa_id}", headers=headers_jose)
    assert resposta.status_code == 404, resposta.text


#put - test
def test_atualizar_tarefa_parcial(client, headers):
    criada = client.post(
        "/tarefas/nova_tarefa",
        headers=headers,
        json={"nome": "test", "descricao": "teste"},
    )
    assert criada.status_code == 201, criada.text
    tarefa_id = criada.json()["id"]

    resposta = client.put(
        f"/tarefas/atualizar_tarefa/{tarefa_id}",
        headers=headers,
        json={"status": "concluido"},
    )

    assert resposta.status_code == 200, resposta.text
    corpo = resposta.json()

    assert corpo["nome"] == "test"
    assert corpo["descricao"] == "teste"
    assert corpo["status"] == "concluido"


def test_atualizar_tarefa_campos_nulos_nao_sobrescrevem(client, headers):
    criada = client.post(
        "/tarefas/nova_tarefa",
        headers=headers,
        json={"nome": "test", "descricao": "teste"},
    )
    assert criada.status_code == 201, criada.text
    tarefa_id = criada.json()["id"]

    resposta = client.put(
        f"/tarefas/atualizar_tarefa/{tarefa_id}",
        headers=headers,
        json={"nome": None, "descricao": None},
    )

    assert resposta.status_code == 200, resposta.text
    corpo = resposta.json()

    assert corpo["nome"] == "test"
    assert corpo["descricao"] == "teste"


def test_atualizar_tarefa_de_outro_usuario_retorna_404(
    client, headers, criar_usuario, autenticar
):
    criada = client.post(
        "/tarefas/nova_tarefa",
        headers=headers,
        json={"nome": "test", "descricao": "teste"},
    )
    assert criada.status_code == 201, criada.text
    tarefa_id = criada.json()["id"]

    criar_usuario(nome="Bia", email="bia@example.com", senha="senha123")
    headers_bia = autenticar(email="bia@example.com")

    resposta = client.put(
        f"/tarefas/atualizar_tarefa/{tarefa_id}",
        headers=headers_bia,
        json={"nome": "alterada pela bia"},
    )

    assert resposta.status_code == 404, resposta.text


def test_atualizar_tarefa_deletada_retorna_404(client, headers):
    criada = client.post(
        "/tarefas/nova_tarefa",
        headers=headers,
        json={"nome": "test", "descricao": "teste"},
    )
    assert criada.status_code == 201, criada.text
    tarefa_id = criada.json()["id"]

    deletada = client.delete(
        f"/tarefas/deletar_tarefa/{tarefa_id}",
        headers=headers,
    )
    assert deletada.status_code == 204, deletada.text

    resposta = client.put(
        f"/tarefas/atualizar_tarefa/{tarefa_id}",
        headers=headers,
        json={"nome": "alterada"},
    )

    assert resposta.status_code == 404, resposta.text


def test_atualizar_tarefa_status_invalido_retorna_422(client, headers):
    criada = client.post(
        "/tarefas/nova_tarefa",
        headers=headers,
        json={"nome": "test", "descricao": "teste"},
    )
    assert criada.status_code == 201, criada.text
    tarefa_id = criada.json()["id"]

    resposta = client.put(
        f"/tarefas/atualizar_tarefa/{tarefa_id}",
        headers=headers,
        json={"status": "abacate"},
    )

    assert resposta.status_code == 422, resposta.text


#patch - test
def test_cancelar_tarefa(client, headers):
    criada = client.post(
        "/tarefas/nova_tarefa",
        headers=headers,
        json={"nome": "test", "descricao": "teste"},
    )
    assert criada.status_code == 201, criada.text
    tarefa_id = criada.json()["id"]

    resposta = client.patch(
        f"/tarefas/cancelar_tarefa/{tarefa_id}",
        headers=headers,
    )

    assert resposta.status_code == 200, resposta.text
    assert resposta.json()["status"] == "cancelado"


def test_cancelar_tarefa_de_outro_usuario_retorna_404(
    client, headers, criar_usuario, autenticar
):
    criada = client.post(
        "/tarefas/nova_tarefa",
        headers=headers,
        json={"nome": "test", "descricao": "teste"},
    )
    assert criada.status_code == 201, criada.text
    tarefa_id = criada.json()["id"]

    criar_usuario(nome="Bia", email="bia@example.com", senha="senha123")
    headers_bia = autenticar(email="bia@example.com")

    resposta = client.patch(
        f"/tarefas/cancelar_tarefa/{tarefa_id}",
        headers=headers_bia,
    )

    assert resposta.status_code == 404, resposta.text


def test_cancelar_tarefa_deletada_retorna_404(client, headers):
    criada = client.post(
        "/tarefas/nova_tarefa",
        headers=headers,
        json={"nome": "test", "descricao": "teste"},
    )
    assert criada.status_code == 201, criada.text
    tarefa_id = criada.json()["id"]

    deletada = client.delete(
        f"/tarefas/deletar_tarefa/{tarefa_id}",
        headers=headers,
    )
    assert deletada.status_code == 204, deletada.text

    resposta = client.patch(
        f"/tarefas/cancelar_tarefa/{tarefa_id}",
        headers=headers,
    )

    assert resposta.status_code == 404, resposta.text


#delete - test
def test_deletar_tarefa_ja_deletada_retorna_404(client, headers):
    criada = client.post(
        "/tarefas/nova_tarefa",
        headers=headers,
        json={"nome": "test", "descricao": "teste"},
    )
    assert criada.status_code == 201, criada.text
    tarefa_id = criada.json()["id"]

    deletada = client.delete(
        f"/tarefas/deletar_tarefa/{tarefa_id}",
        headers=headers,
    )
    assert deletada.status_code == 204, deletada.text

    resposta = client.delete(
        f"/tarefas/deletar_tarefa/{tarefa_id}",
        headers=headers,
    )

    assert resposta.status_code == 404, resposta.text


def test_deletar_tarefa_preserva_linha_no_banco(client, headers, db_session):
    criada = client.post(
        "/tarefas/nova_tarefa",
        headers=headers,
        json={"nome": "test", "descricao": "teste"},
    )
    assert criada.status_code == 201, criada.text
    tarefa_id = criada.json()["id"]

    resposta = client.delete(
        f"/tarefas/deletar_tarefa/{tarefa_id}",
        headers=headers,
    )
    assert resposta.status_code == 204, resposta.text

    db_session.expire_all()
    tarefa = db_session.get(Tarefa, tarefa_id)

    assert tarefa is not None
    assert tarefa.deletado is True


def test_deletar_tarefa_de_outro_usuario_retorna_404(
    client, headers, criar_usuario, autenticar
):
    criada = client.post(
        "/tarefas/nova_tarefa",
        headers=headers,
        json={"nome": "test", "descricao": "teste"},
    )
    assert criada.status_code == 201, criada.text
    tarefa_id = criada.json()["id"]

    criar_usuario(nome="Bia", email="bia@example.com", senha="senha123")
    headers_bia = autenticar(email="bia@example.com")

    resposta = client.delete(
        f"/tarefas/deletar_tarefa/{tarefa_id}",
        headers=headers_bia,
    )
    assert resposta.status_code == 404, resposta.text

    resposta = client.get(
        f"/tarefas/tarefa/{tarefa_id}",
        headers=headers,
    )
    assert resposta.status_code == 200, resposta.text
