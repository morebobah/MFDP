from sqlalchemy.orm import Mapped, relationship
from database.database import Base, int_pk, str_uniq, bool_val


class User(Base):
    __tablename__='users'
    
    id: Mapped[int_pk]
    email: Mapped[str_uniq]
    first_name: Mapped[str]
    last_name: Mapped[str]
    password: Mapped[str]
    is_access: Mapped[bool_val]
    is_admin: Mapped[bool_val]
    packets: Mapped[list["Packet"]] = relationship(back_populates="user") 

    extend_existing = True

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(id={self.id})"
    
    def __str__(self) -> str:
        return f"{self.id} - {self.first_name} {self.last_name}"
  