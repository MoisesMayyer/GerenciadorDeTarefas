from enum import StrEnum

from sqlalchemy import Column, Enum as SAEnum, Integer, String, Boolean, ForeignKey
from sqlalchemy.orm import relationship

from app.database.database import Base


class StatusTarefa(StrEnum):


    PENDENTE = "pendente"
    CONCLUIDO = "concluido"
    CANCELADO = "cancelado"


class Tarefa(Base):
    __tablename__ = "tarefas"

    id = Column("id", Integer, primary_key=True, autoincrement=True, nullable=False)
    nome = Column("nome", String, nullable=False)
    descricao = Column("descricao", String)
    status = Column(
        "status",
        SAEnum(
            StatusTarefa,
            name="status_tarefa",
            native_enum=False,
            values_callable=lambda enum_class: [membro.value for membro in enum_class],
            create_constraint=True,
        ),
        nullable=False,
        default=StatusTarefa.PENDENTE,
    )
    usuario_id = Column("usuario_id", Integer, ForeignKey("usuarios.id"))

    usuario = relationship("Usuario", back_populates="tarefas")


class Usuario(Base):
    __tablename__ = "usuarios"

    id = Column("id", Integer, primary_key=True, autoincrement=True, nullable=False)
    nome = Column("nome", String, nullable=False)
    email = Column("email", String, nullable=False)
    senha = Column("senha", String, nullable=False)
    ativo = Column("ativo", Boolean, nullable=False, default=True)

    tarefas = relationship("Tarefa", back_populates="usuario")