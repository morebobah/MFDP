from models.event import Event
from sqlalchemy import select
from sqlalchemy.exc import SQLAlchemyError
from pydantic import BaseModel
from services.crud.exceptions import InsufficientFunds
from database.database import session_maker


class EventsCRUD:
    model = Event
    
    @classmethod
    def find_all(cls):
        with session_maker() as session:
            query = select(cls.model).order_by(cls.model.id.desc())
            rows = session.execute(query)
            return rows.scalars().all()
    
    @classmethod
    def find_several(cls, filters: BaseModel):
        filter_dict = filters.model_dump(exclude_unset=True)
        with session_maker() as session:
            query = select(cls.model).filter_by(**filter_dict).order_by(cls.model.id.desc())
            rows = session.execute(query)
            return rows.scalars().all()
        
    @classmethod
    def find_one_or_none(cls, filters: BaseModel):
        filter_dict = filters.model_dump(exclude_unset=True)
        with session_maker() as session:
            try:
                query = select(cls.model).filter_by(**filter_dict)
                result = session.execute(query)
                record = result.scalar_one_or_none()
                return record
            except SQLAlchemyError as e:
                raise

    
    @classmethod
    def add(cls, values: BaseModel):
        values_dict = values.model_dump(exclude_unset=True)
        new_instance = cls.model(**values_dict)
        with session_maker() as session:
            session.add(new_instance)
            try:
                session.commit()
                session.refresh(new_instance)
            except SQLAlchemyError as e:
                session.rollback()
                raise e
        return new_instance
    
    @classmethod
    def update(cls, id: BaseModel, target: BaseModel):
        filter_dict = id.model_dump(exclude_unset=True)
        with session_maker() as session:
            try:
                query = select(cls.model).filter_by(**filter_dict)
                result = session.execute(query)
                record = result.scalar_one_or_none()
                record.target = target.target               
                session.commit()
                session.refresh(record)
                return record
            except SQLAlchemyError as e:
                raise


    @classmethod
    def updateSeveral(cls, id: BaseModel, update_data: BaseModel):
        filter_dict = id.model_dump(exclude_unset=True)
        update_dict = update_data.model_dump(exclude_unset=True)
        
        with session_maker() as session:
            try:
                query = select(cls.model).filter_by(**filter_dict)
                result = session.execute(query)
                record = result.scalar_one_or_none()
                
                if record is None:
                    raise ValueError("Record not found")
                
                # Обновляем все поля из update_data
                for field, value in update_dict.items():
                    if field != 'id':
                        setattr(record, field, value)
                    
                session.commit()
                session.refresh(record)
                return record
            except SQLAlchemyError as e:
                session.rollback()
                raise