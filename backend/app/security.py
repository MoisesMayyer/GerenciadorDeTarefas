import hashlib
import secrets
from datetime import datetime, timedelta, timezone

import jwt
from pwdlib import PasswordHash

from app.config import settings

password_hash = PasswordHash.recommended()


def agora_utc() -> datetime:
    return datetime.now(timezone.utc)


def gerar_token_refresh() -> str:
    return secrets.token_urlsafe(48)


def hash_token_refresh(token: str) -> str:
    return hashlib.sha256(token.encode("utf-8")).hexdigest()


def hash_senha(senha: str) -> str:
    return password_hash.hash(senha)


def verificar_senha(senha: str, senha_hash: str) -> bool:
    return password_hash.verify(senha, senha_hash)


def criar_token_access(dados: dict[str, object]) -> str:
    payload = dados.copy()
    payload["tipo"] = "access"
    payload["exp"] = agora_utc() + timedelta(
        minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
    )
    return jwt.encode(payload, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
