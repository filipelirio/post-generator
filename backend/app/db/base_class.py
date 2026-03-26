from typing import Any
from sqlalchemy.orm import DeclarativeBase, declared_attr

class Base(DeclarativeBase):
    id: Any
    __name__: str

    # Gera o nome da tabela automaticamente a partir do nome da classe
    @declared_attr
    def __tablename__(cls) -> str:
        return cls.__name__.lower()
