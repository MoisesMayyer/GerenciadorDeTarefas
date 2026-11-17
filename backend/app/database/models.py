from enum import StrEnum

from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    Enum as SAEnum,
    ForeignKey,
    Integer,
    String,
)
from sqlalchemy.orm import relationship

from app.database.database import Base
from app.database.mixins import TimestampMixin

class StatusTarefa(StrEnum):


    PENDENTE = "pendente"
    CONCLUIDO = "concluido"
    CANCELADO = "cancelado"


class Tarefa(Base, TimestampMixin):
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
    usuario_id = Column("usuario_id", Integer,ForeignKey("usuarios.id", ondelete="CASCADE"), nullable=False, index=True,)
    deletado = Column("deletado", Boolean, nullable=False, default=False)

    usuario = relationship("Usuario", back_populates="tarefas")


class Usuario(Base, TimestampMixin):
    __tablename__ = "usuarios"

    id = Column("id", Integer, primary_key=True, autoincrement=True, nullable=False)
    nome = Column("nome", String, nullable=False)
    email = Column("email", String, nullable=False, unique=True, index=True)
    senha = Column("senha", String, nullable=False)
    ativo = Column("ativo", Boolean, nullable=False, default=True)

    tarefas = relationship(
        "Tarefa", back_populates="usuario", cascade="all, delete-orphan"
    )
    refresh_tokens = relationship(
        "RefreshToken", back_populates="usuario", cascade="all, delete-orphan"
    )


class RefreshToken(Base, TimestampMixin):
    __tablename__ = "refresh_tokens"

    id = Column("id", Integer, primary_key=True, autoincrement=True, nullable=False)
    token_hash = Column(
        "token_hash", String(64), nullable=False, unique=True, index=True
    )
    usuario_id = Column(
        "usuario_id",
        Integer,
        ForeignKey("usuarios.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    expira_em = Column("expira_em", DateTime(timezone=True), nullable=False)
    revogado = Column("revogado", Boolean, nullable=False, default=False)

    usuario = relationship("Usuario", back_populates="refresh_tokens")