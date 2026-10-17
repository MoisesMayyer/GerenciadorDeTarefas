from typing import Optional

from pydantic import BaseModel, ConfigDict

from app.database.models import StatusTarefa


class TarefaBase(BaseModel):
    nome: str
    descricao: str


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
