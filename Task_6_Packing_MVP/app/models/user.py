from sqlalchemy import text
from sqlalchemy import event
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.orm import Mapped, mapped_column
from database.database import Base, int_pk, str_uniq, float_zero, float_one, bool_val

class User(Base):
    __tablename__='users'
    
    id: Mapped[int_pk]
    email: Mapped[str_uniq]
    first_name: Mapped[str]
    last_name: Mapped[str]
    password: Mapped[str]
    is_admin: Mapped[bool_val]

    extend_existing = True

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(id={self.id})"
    
    def __str__(self) -> str:
        return f"{self.id} - {self.first_name} {self.last_name}"
  