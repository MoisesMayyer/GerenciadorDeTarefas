from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.depends import get_db, verificar_token
from app.database.models import StatusTarefa, Tarefa, Usuario
from app.schemas.tarefas import TarefaResponse, TarefaCreate, TarefaUpdate

rota_tarefas = APIRouter(prefix="/tarefas", tags=["Tarefas"])


@rota_tarefas.get("/", response_model=list[TarefaResponse])
def pegar_tarefas(
    db: Session = Depends(get_db), usuario: Usuario = Depends(verificar_token)
):
    return db.query(Tarefa).filter(Tarefa.usuario_id == usuario.id).all()


@rota_tarefas.get("/tarefa/{id}", response_model=TarefaResponse)
def pegar_tarefa_id(
    id: int, db: Session = Depends(get_db), usuario: Usuario = Depends(verificar_token)
):
    tarefa_existe = (
        db.query(Tarefa)
        .filter(Tarefa.id == id, Tarefa.usuario_id == usuario.id)
        .first()
    )

    if not tarefa_existe:
        raise HTTPException(status_code=404, detail="tarefa nao encontrada")

    return tarefa_existe


@rota_tarefas.post("/nova_tarefa", response_model=TarefaResponse, status_code=201)
def adicionar_tarefa(
    dados: TarefaCreate,
    db: Session = Depends(get_db),
    usuario: Usuario = Depends(verificar_token),
):
    tarefa = Tarefa(
        nome=dados.nome,
        descricao=dados.descricao,
        status=dados.status,
        usuario_id=usuario.id,
    )

    db.add(tarefa)
    db.commit()
    db.refresh(tarefa)

    return tarefa


@rota_tarefas.put("/atualizar_tarefa/{id}", response_model=TarefaResponse)
def atualizar_tarefa(
    id: int,
    dados: TarefaUpdate,
    db: Session = Depends(get_db),
    usuario: Usuario = Depends(verificar_token),
):
    tarefa_existe = (
        db.query(Tarefa)
        .filter(Tarefa.id == id, Tarefa.usuario_id == usuario.id)
        .first()
    )

    if not tarefa_existe:
        raise HTTPException(status_code=404, detail="tarefa nao encontrada")

    for campo, valor in dados.model_dump(exclude_unset=True, exclude_none=True).items():
        setattr(tarefa_existe, campo, valor)

    db.commit()
    db.refresh(tarefa_existe)

    return tarefa_existe


@rota_tarefas.patch("/cancelar_tarefa/{id}", response_model=TarefaResponse)
def cancelar_tarefa(
    id: int, db: Session = Depends(get_db), usuario: Usuario = Depends(verificar_token)
):
    tarefa_existe = (
        db.query(Tarefa)
        .filter(Tarefa.id == id, Tarefa.usuario_id == usuario.id)
        .first()
    )

    if not tarefa_existe:
        raise HTTPException(status_code=404, detail="tarefa nao encontrada")
    tarefa_existe.status = StatusTarefa.CANCELADO

    db.commit()
    db.refresh(tarefa_existe)

    return tarefa_existe


@rota_tarefas.delete("/deletar_tarefa/{id}", status_code=204)
def deletar_tarefa(
    id: int, db: Session = Depends(get_db), usuario: Usuario = Depends(verificar_token)
):
    tarefa_existe = (
        db.query(Tarefa)
        .filter(Tarefa.id == id, Tarefa.usuario_id == usuario.id)
        .first()
    )

    if not tarefa_existe:
        raise HTTPException(status_code=404, detail="tarefa nao encontrada")

    db.delete(tarefa_existe)
    db.commit()