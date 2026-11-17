from datetime import timedelta

from fastapi import APIRouter, Depends, HTTPException, Response
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from app.config import settings
from app.database.models import RefreshToken, Usuario
from app.depends import get_db, verificar_token
from app.schemas.token import RefreshTokenRequest, Token
from app.schemas.usuarios import UsuarioResponse
from app.security import (
    agora_utc,
    criar_token_access,
    gerar_token_refresh,
    hash_token_refresh,
    verificar_senha,
)

router_auth = APIRouter(prefix="/auth", tags=["Autenticação"])


def _criar_refresh_token(db: Session, usuario: Usuario) -> str:
    token = gerar_token_refresh()

    db.add(
        RefreshToken(
            token_hash=hash_token_refresh(token),
            usuario_id=usuario.id,
            expira_em=agora_utc()
            + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS),
        )
    )

    return token


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

    access_token = criar_token_access({"sub": str(usuario.id)})
    refresh_token = _criar_refresh_token(db, usuario)
    db.commit()

    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer",
    }


@router_auth.post("/refresh", response_model=Token)
def refresh(dados: RefreshTokenRequest, db: Session = Depends(get_db)):
    registro = (
        db.query(RefreshToken)
        .filter(RefreshToken.token_hash == hash_token_refresh(dados.refresh_token))
        .first()
    )

    if (
        not registro
        or registro.revogado
        or registro.expira_em <= agora_utc()
    ):
        raise HTTPException(status_code=401, detail="Refresh token inválido")

    usuario = db.query(Usuario).filter(Usuario.id == registro.usuario_id).first()

    if not usuario or not usuario.ativo:
        raise HTTPException(status_code=401, detail="Refresh token inválido")

    registro.revogado = True
    access_token = criar_token_access({"sub": str(usuario.id)})
    refresh_token = _criar_refresh_token(db, usuario)
    db.commit()

    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer",
    }


@router_auth.post("/logout", status_code=204)
def logout(dados: RefreshTokenRequest, db: Session = Depends(get_db)):
    registro = (
        db.query(RefreshToken)
        .filter(RefreshToken.token_hash == hash_token_refresh(dados.refresh_token))
        .first()
    )

    if registro and not registro.revogado:
        registro.revogado = True
        db.commit()

    return Response(status_code=204)


@router_auth.get("/me", response_model=UsuarioResponse)
def get_user(usuario: Usuario = Depends(verificar_token)):
    return usuario
