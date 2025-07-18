from models.user import User
from sqlalchemy import select
from sqlalchemy.exc import SQLAlchemyError
from pydantic import BaseModel
from services.crud.exceptions import InsufficientFunds
from database.database import session_maker

class UsersCRUD:
    model = User
    
    @classmethod
    def find_all_users(cls):
        with session_maker() as session:
            query = select(User).order_by(cls.model.id.desc())
            users = session.execute(query)
            return users.scalars().all()
    
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
    def find_one_or_none_by_email(cls, filters: BaseModel):
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
    def find_one_or_none_by_id(cls, filters: BaseModel):
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
    def get_balance_by_id(cls, id: BaseModel):
        return cls.find_one_or_none_by_id(id).balance
    
    @classmethod
    def add(cls, values: BaseModel):
        values_dict = values.model_dump(exclude_unset=True)
        new_instance = cls.model(**values_dict)
        with session_maker() as session:
            session.add(new_instance)
            try:
                session.commit()
            except SQLAlchemyError as e:
                session.rollback()
                raise e
        return new_instance
    
    @classmethod
    def allow_admin_by_id(cls, id: BaseModel):
        with session_maker() as session:
            try:
                query = select(cls.model).filter_by(id=id)
                result = session.execute(query)
                record = result.scalar_one_or_none()
                if record is not None:
                    record.is_admin = True
                session.commit()
                session.refresh(record)
                return record
            except SQLAlchemyError as e:
                raise

    @classmethod
    def allow_admin_by_email(cls, email: BaseModel):
        with session_maker() as session:
            try:
                query = select(cls.model).filter_by(email=email)
                result = session.execute(query)
                record = result.scalar_one_or_none()
                if record is not None:
                    record.is_admin = True
                session.commit()
                session.refresh(record)
                return record
            except SQLAlchemyError as e:
                raise
    
    @classmethod
    def disallow_admin_by_id(cls, id: BaseModel):
        with session_maker() as session:
            try:
                query = select(cls.model).filter_by(id=id)
                result = session.execute(query)
                record = result.scalar_one_or_none()
                if record is not None:
                    record.is_admin = False
                session.commit()
                session.refresh(record)
                return record
            except SQLAlchemyError as e:
                raise

    @classmethod
    def disallow_admin_by_email(cls, email: BaseModel):
        with session_maker() as session:
            try:
                query = select(cls.model).filter_by(email=email)
                result = session.execute(query)
                record = result.scalar_one_or_none()
                if record is not None:
                    record.is_admin = False
                session.commit()
                session.refresh(record)
                return record
            except SQLAlchemyError as e:
                raise

    @classmethod
    def add_payment_by_id(cls, filters: BaseModel, pay: BaseModel):
        filter_dict = filters.model_dump(exclude_unset=True)
        with session_maker() as session:
            try:
                query = select(cls.model).filter_by(**filter_dict)
                result = session.execute(query)
                record = result.scalar_one_or_none()
                record.balance += pay
                session.commit()
                session.refresh(record)
                return record
            except SQLAlchemyError as e:
                raise

    @classmethod
    def add_payment_by_email(cls, email: BaseModel, pay: BaseModel):
        with session_maker() as session:
            try:
                query = select(cls.model).filter_by(email = email)
                result = session.execute(query)
                record = result.scalar_one_or_none()
                record.balance += pay
                session.commit()
                session.refresh(record)
                return record
            except SQLAlchemyError as e:
                raise

    @classmethod
    def spend_payment_by_id(cls, id: BaseModel, pay: BaseModel):
        if pay>=0:
            raise ValueError

        with session_maker() as session:
            try:
                query = select(cls.model).filter_by(id = id)
                result = session.execute(query)
                record = result.scalar_one_or_none()
                if record.balance + pay < 0:
                    raise InsufficientFunds
                record.balance += pay                
                session.commit()
                session.refresh(record)
                return record
            except SQLAlchemyError as e:
                raise

    @classmethod
    def spend_payment_by_email(cls, email: BaseModel, pay: BaseModel):
        if pay>=0:
            raise ValueError
        
        with session_maker() as session:
            try:
                query = select(cls.model).filter_by(email = email)
                result = session.execute(query)
                record = result.scalar_one_or_none()
                if record.balance + pay < 0:
                    raise InsufficientFunds
                
                record.balance += pay
                session.commit()
                session.refresh(record)
                return record
            except SQLAlchemyError as e:
                raise