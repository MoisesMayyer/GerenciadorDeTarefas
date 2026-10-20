from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from app.depends import get_db, verificar_token
from app.database.models import Usuario
from app.schemas.token import Token
from app.schemas.usuarios import UsuarioResponse
from app.security import criar_token_access, verificar_senha

router_auth = APIRouter(prefix="/auth", tags=["Autenticação"])


@router_auth.post("/login", response_model=Token)
def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db),
):
    email = form_data.username.strip().lower()
    usuario = db.query(Usuario).filter(Usuario.email == email).first()

    if not usuario:
        raise HTTPException(status_code=401, detail="Credenciais inválidas")

    if not usuario.ativo:
        raise HTTPException(status_code=401, detail="Credenciais inválidas")

    if not verificar_senha(form_data.password, usuario.senha):
        raise HTTPException(status_code=401, detail="Credenciais inválidas")

    token = criar_token_access({"sub": str(usuario.id)})

    return {"access_token": token, "token_type": "bearer"}


@router_auth.get("/me", response_model=UsuarioResponse)
def get_user(usuario: Usuario = Depends(verificar_token)):
    return usuario
