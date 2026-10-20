from typing import Optional

from pydantic import BaseModel, ConfigDict, EmailStr, Field, field_validator


class UsuarioBase(BaseModel):
    nome: str = Field(..., min_length=1, max_length=50, description="Nome do usuario")


class UsuarioCreate(UsuarioBase):
    email: EmailStr = Field(..., description="Email do usuario")
    senha: str = Field(..., min_length=6, max_length=128, description="Senha do usuario")

    @field_validator("email")
    @classmethod
    def normalizar_email(cls, valor: EmailStr) -> str:
        return valor.strip().lower()

    @field_validator("senha")
    @classmethod
    def validar_senha(cls, valor: str) -> str:
        if not valor.strip():
            raise ValueError("A senha não pode conter apenas espaços")

        return valor


class UsuarioUpdate(BaseModel):
    nome: Optional[str] = Field(None, description="Nome do usuario")
    email: Optional[EmailStr] = Field(None, description="Email do usuario")
    ativo: Optional[bool] = Field(None, description="Ativo do usuario")


class UsuarioResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    nome: str
    email: EmailStr
    ativo: bool
