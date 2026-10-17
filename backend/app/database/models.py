from enum import StrEnum

from sqlalchemy import Column, Enum as SAEnum, Integer, String

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
