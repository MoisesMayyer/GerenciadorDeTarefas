from typing import Optional

from pydantic import BaseModel, ConfigDict, Field, field_validator

from app.database.models import StatusTarefa


class TarefaBase(BaseModel):
    nome: str = Field(..., min_length=1)
    descricao: str

    @field_validator("nome")
    @classmethod
    def validar_nome(cls, valor: str) -> str:
        valor = valor.strip()

        if not valor:
            raise ValueError("O nome não pode ser vazio")

        return valor


class TarefaCreate(TarefaBase):
    status: StatusTarefa = StatusTarefa.PENDENTE


class TarefaUpdate(BaseModel):
    nome: Optional[str] = None
    descricao: Optional[str] = None
    status: Optional[StatusTarefa] = None


class TarefaResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    nome: str
    descricao: str
    status: StatusTarefa
