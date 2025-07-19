import uuid
from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from database.database import Base, int_pk, str_uniq, float_zero, float_one, bool_val

class Packet(Base):
    __tablename__ = 'packets'
    
    id: Mapped[int_pk]
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    uname: Mapped[str] = mapped_column(unique=True, default=lambda: str(uuid.uuid4()))
    aname: Mapped[str]
    status: Mapped[str] = mapped_column(default="created")

    user: Mapped["User"] = relationship(back_populates="packets")
    events: Mapped[list["Event"]] = relationship(back_populates="packet")
    
    extend_existing = True

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(id={self.id})"
    
    def __str__(self) -> str:
        return f"{self.id} - {self.uname} {self.aname}"