from pydantic import BaseModel, EmailStr, Field, field_validator
from typing import Optional


class UsuarioBase(BaseModel):
    nome: str = Field(...,min_length=1,max_length=50, description="Nome do usuario")


class UsuarioCreate(UsuarioBase):
    email: EmailStr = Field(..., description="Email do usuario")
    senha: str = Field(...,min_length=6, max_length=12,description="Senha do usuario")

    @field_validator("senha")
    @classmethod
    def validar_titulo(cls, valor):
        if valor is not None and not valor.strip():
            raise ValueError("A senha não pode conter apenas espaços")

        return valor


class UsuarioUpdate(BaseModel):
    nome: Optional[str] = Field(None, description="Nome do usuario")
    email: Optional[str] = Field(None, description="Email do usuario")
    ativo: Optional[bool] = Field(None, description="Ativo do usuario")


class UsuarioResponse(BaseModel):
    id: int
    nome: str
    email: EmailStr
    ativo: bool
