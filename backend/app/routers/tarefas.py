from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import Optional

from app.depends import get_db, verificar_token
from app.database.models import StatusTarefa, Tarefa, Usuario
from app.schemas.tarefas import TarefaResponse, TarefaCreate, TarefaUpdate, TarefaListResponse

rota_tarefas = APIRouter(prefix="/tarefas", tags=["Tarefas"])


@rota_tarefas.get("/", response_model=TarefaListResponse)
def pegar_tarefas(
    db: Session = Depends(get_db),
    usuario: Usuario = Depends(verificar_token),
    skip: int = Query(0,ge=0),
    limit:int = Query(10, ge=1, le=100),
    busca: Optional[str] = Query(None),
):
    query = db.query(Tarefa).filter(Tarefa.usuario_id == usuario.id, Tarefa.deletado.is_(False))

    if busca:
        query = query.filter(Tarefa.descricao.ilike(f"%{busca}%"))

    total = query.count()

    tarefas = (
        query.order_by(Tarefa.id.desc())
        .offset(skip)
        .limit(limit)
        .all()
    )

    return TarefaListResponse(
        items =[TarefaResponse.model_validate(t) for t in tarefas],
        skip=skip,
        total = total,
        limit = limit,
    )


@rota_tarefas.get("/tarefa/{id}", response_model=TarefaResponse)
def pegar_tarefa_id(
    id: int, db: Session = Depends(get_db), usuario: Usuario = Depends(verificar_token)
):
    tarefa_existe = (
        db.query(Tarefa)
        .filter(
            Tarefa.id == id,
            Tarefa.usuario_id == usuario.id,
            Tarefa.deletado.is_(False),
        )
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
        .filter(
            Tarefa.id == id,
            Tarefa.usuario_id == usuario.id,
            Tarefa.deletado.is_(False),
        )
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
        .filter(
            Tarefa.id == id,
            Tarefa.usuario_id == usuario.id,
            Tarefa.deletado.is_(False),
        )
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
        .filter(
            Tarefa.id == id,
            Tarefa.usuario_id == usuario.id,
            Tarefa.deletado.is_(False),
        )
        .first()
    )

    if not tarefa_existe:
        raise HTTPException(status_code=404, detail="tarefa nao encontrada")

    tarefa_existe.deletado = True

    db.commit()