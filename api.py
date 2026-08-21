from fastapi import FastAPI

from pydantic import BaseModel

from tarefas import Tarefas
app = FastAPI()


class Tarefa(BaseModel):
    id: int
    tarefa: str
    status: str


class CriarTarefa(BaseModel):
    descricao:  str


class AtualizarTarefas(BaseModel):
    descricao: str | None = None
    status: str | None = None


@app.get("/")
def home():
    return "Bem vindo a API de gerenciador de tarefas"


@app.get("/tarefas")
def pegar_tarefas():
    tarefas = Tarefas()

    return tarefas.listar_tarefas()


@app.get("/tarefas/{identificacao}")
def pegar_tarefa_id(identificacao: int):
    tarefas = Tarefas()

    return tarefas.buscar_por_id(identificacao)


@app.put("/atualizar_tarefa/{identificacao}")
def atualizar_tarefa(
    identificacao: int,
    tarefa: AtualizarTarefas,
):
    tarefas = Tarefas()

    tarefa_atualizada = tarefas.atualizar_tarefa(
        identificacao,
        tarefa.descricao,
        tarefa.status,
    )

    return tarefa_atualizada


@app.delete("/deletar_tarefa/{identificacao}")
def deletar_tarefa(identificacao: int):
    tarefas = Tarefas()

    return tarefas.deletar_tarefa(identificacao)