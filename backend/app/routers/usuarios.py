from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.database.models import Usuario
from app.depends import get_db, verificar_token
from app.schemas.usuarios import UsuarioCreate, UsuarioResponse, UsuarioUpdate
from app.security import hash_senha

router_usuarios = APIRouter(prefix="/usuarios", tags=["Usuários"])


# Sem papel de admin, cada usuario enxerga apenas a propria conta.
@router_usuarios.get("/", response_model=list[UsuarioResponse])
def listar_usuarios(usuario: Usuario = Depends(verificar_token)):
    return [usuario]


@router_usuarios.get("/{id}", response_model=UsuarioResponse)
def pegar_usuario(id: int, usuario: Usuario = Depends(verificar_token)):
    if id != usuario.id:
        raise HTTPException(status_code=404, detail="usuario nao encontrado")

    return usuario


@router_usuarios.post("/", response_model=UsuarioResponse, status_code=201)
def criar_usuario(dados: UsuarioCreate, db: Session = Depends(get_db)):
    email_existe = db.query(Usuario).filter(Usuario.email == dados.email).first()

    if email_existe:
        raise HTTPException(status_code=409, detail="email ja cadastrado")

    usuario = Usuario(
        nome=dados.nome,
        email=dados.email,
        senha=hash_senha(dados.senha),
    )

    db.add(usuario)

    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=409, detail="email ja cadastrado")

    db.refresh(usuario)

    return usuario


@router_usuarios.put("/{id}", response_model=UsuarioResponse)
def atualizar_usuario(
    id: int,
    dados: UsuarioUpdate,
    db: Session = Depends(get_db),
    usuario: Usuario = Depends(verificar_token),
):
    if id != usuario.id:
        raise HTTPException(status_code=404, detail="usuario nao encontrado")

    campos = dados.model_dump(exclude_unset=True, exclude_none=True)

    if "email" in campos and campos["email"] != usuario.email:
        email_existe = (
            db.query(Usuario)
            .filter(Usuario.email == campos["email"], Usuario.id != usuario.id)
            .first()
        )

        if email_existe:
            raise HTTPException(status_code=409, detail="email ja cadastrado")

    if "senha" in campos:
        usuario.senha = hash_senha(campos.pop("senha"))

    for campo, valor in campos.items():
        setattr(usuario, campo, valor)

    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=409, detail="email ja cadastrado")

    db.refresh(usuario)

    return usuario


@router_usuarios.patch("/{id}/cancelar", response_model=UsuarioResponse)
def cancelar_usuario(
    id: int, db: Session = Depends(get_db), usuario: Usuario = Depends(verificar_token)
):
    if id != usuario.id:
        raise HTTPException(status_code=404, detail="usuario nao encontrado")

    usuario.ativo = False
    db.commit()
    db.refresh(usuario)

    return usuario


@router_usuarios.delete("/{id}", status_code=204)
def deletar_usuario(
    id: int, db: Session = Depends(get_db), usuario: Usuario = Depends(verificar_token)
):
    if id != usuario.id:
        raise HTTPException(status_code=404, detail="usuario nao encontrado")

    db.delete(usuario)
    db.commit()
