from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.database.models import Usuario
from app.depends import get_db
from app.schemas.usuarios import UsuarioCreate, UsuarioResponse
from app.security import hash_senha

router_usuarios = APIRouter(prefix="/usuarios", tags=["Usuários"])


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
