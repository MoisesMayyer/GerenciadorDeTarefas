from sqlalchemy import Column, DateTime, func


class TimestampMixin:
    criado_em = Column("criado_em", DateTime, server_default=func.now(), nullable=False)
    atualizado_em = Column("atualizado_em", DateTime, server_default=func.now(), onupdate=func.now(), nullable=False)