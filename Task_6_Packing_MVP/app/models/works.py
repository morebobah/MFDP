from sqlalchemy.orm import Mapped, mapped_column
from database.database import Base, int_pk
from datetime import datetime

class Works(Base):
    __tablename__ = 'works'

    id: Mapped[int_pk]
    packet: Mapped[int] = mapped_column(nullable=False)  # Номер пакета
    year: Mapped[int] = mapped_column(nullable=False)
    type_of_work: Mapped[float] = mapped_column(nullable=False) #Бинарный принзнак новый или существующий
    contractor: Mapped[float] = mapped_column(nullable=False)
    idleft: Mapped[int] = mapped_column(nullable=False)
    idright: Mapped[int] = mapped_column(nullable=False)
    g2: Mapped[float] = mapped_column(nullable=False)  # 2g, бинарный
    g3: Mapped[float] = mapped_column(nullable=False)  # 3g, бинарный
    g4: Mapped[float] = mapped_column(nullable=False)  # 4g, бинарный
    rrl: Mapped[float] = mapped_column(nullable=False)  # rrl, бинарный
    a_index: Mapped[int] = mapped_column(nullable=False)  # Признак места размещения объекта
    a_region: Mapped[float] = mapped_column(nullable=False)  # Регион размещения объекта
    a_place: Mapped[float] = mapped_column(nullable=False)  # Признак размещения объекта город или нет (бинарный)
    date_start: Mapped[datetime] = mapped_column(nullable=False)  # Дата и время добавления в систему/начала работ
    adr_prepare: Mapped[datetime] = mapped_column(nullable=False)  # Дата и время добавления в систему/начала работ 
    tech_fin: Mapped[datetime] = mapped_column(nullable=True)  # Дата и время готовности технической части
    equipment_fin: Mapped[datetime] = mapped_column(nullable=True)  # Дата и время заказа оборудования
    equipment_prepared: Mapped[datetime] = mapped_column(nullable=True)  # Дата и время комплектации
    contractor_accepted: Mapped[datetime] = mapped_column(nullable=True)  # Дата и время проектирования
    ready_for_work: Mapped[datetime] = mapped_column(nullable=True)  # Дата и время готовности к пуску
    params_fin: Mapped[datetime] = mapped_column(nullable=True)  # Дата и время готовности параметров
    integration_fin: Mapped[datetime] = mapped_column(nullable=True)  # Дата и время интеграции
    monitoring_fin: Mapped[datetime] = mapped_column(nullable=True)  # Дата и время мониторинга
    commisioning_fin: Mapped[datetime] = mapped_column(nullable=True)  # Дата и время окончания всех работ
    target: Mapped[datetime] = mapped_column(nullable=True)  # Дата и время окончания всех работ

    extend_existing = True

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(id={self.id})" 