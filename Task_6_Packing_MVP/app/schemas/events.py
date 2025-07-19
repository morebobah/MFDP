from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime



class SEvents(BaseModel):
    #2023,0.0,30.0,368838,188,0.0,0.0,1.0,0.0,365013,0.0,1.0,54.44375,83.03888888888889,7.935416666666667,10.665277777777778,7.919444444444444,38.452777777777776,2.18125,11.816666666666666,0.08194444444444444,1.0326388888888889,209.0

    packet_id: int = Field(..., example=1, description="Номер пакета")
    year: int = Field(..., example = 2023)
    type_of_work: float = Field(..., example=0.0, description="0-город, 1-пригород, бинарный")
    contractor: float = Field(..., example=30.0)
    idleft: int = Field(..., example=368838)
    idright: int = Field(..., example=188)
    g2: float = Field(..., example=0.0, description="2g, бинарный")
    g3: float = Field(..., example=0.0, description="3g, бинарный")
    g4: float = Field(..., example=1.0, description="4g, бинарный")
    rrl: float = Field(..., example=0.0, description="rrl, бинарный")
    a_index: int = Field(..., example=365013, description="Признак места размещения объекта")
    a_region: float = Field(..., example=0.0, description="Регион размещения объекта")
    a_place: float = Field(..., example=1.0, description="Признак размещения объекта город или нет (бинарный)")
    date_start: Optional[datetime] = Field(..., description="Дата и время добавления в систему/начала работ")
    adr_prepare: Optional[datetime] = Field(..., description="Дата и время определения места размещения")
    tech_fin: Optional[datetime] = Field(None, description="Дата и время готовности технической части")
    equipment_fin: Optional[datetime] = Field(None, description="Дата и время заказа оборудования")
    equipment_prepared: Optional[datetime] = Field(None, description="Дата и время комплектации")
    contractor_accepted: Optional[datetime] = Field(None, description="Дата и время проектирования")
    ready_for_work: Optional[datetime] = Field(None, description="Дата и время готовности к пуску")
    params_fin: Optional[datetime] = Field(None, description="Дата и время готовности параметров")
    integration_fin: Optional[datetime] = Field(None, description="Дата и время интеграции")
    monitoring_fin: Optional[datetime] = Field(None, description="Дата и время мониторинга")
    commisioning_fin: Optional[datetime] = Field(None, description="Дата и время окончания всех работ")

class STarget(BaseModel):
    target: Optional[datetime] = Field(..., description="Целевая даата")

class SEventID(BaseModel):
    id: int = Field(..., description="Номер мероприятия")