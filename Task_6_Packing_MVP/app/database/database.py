from database.config import get_settings

from datetime import datetime
from typing import Annotated

from sqlalchemy import func, create_engine, text, String
from sqlalchemy.orm import DeclarativeBase, mapped_column
from sqlalchemy.orm import sessionmaker, Session



engine = create_engine(url=get_settings().DATABASE_URL_psycopg, 
                       echo = True, pool_size=5, max_overflow=10)
session_maker = sessionmaker(engine)

def get_session():
    with Session(engine) as session:
        yield session


class Base(DeclarativeBase):
    __abstract__ = True

int_pk = Annotated[int, mapped_column(primary_key=True)]
float_zero = Annotated[float, mapped_column(server_default=text('0.0'), nullable=False)]
float_one = Annotated[float, mapped_column(server_default=text('1.0'), nullable=False)]
bool_val =  Annotated[bool, mapped_column(default=False, server_default=text('false'), nullable=False)]
created_at = Annotated[datetime, mapped_column(server_default=func.now())]
updated_at = Annotated[datetime, mapped_column(server_default=func.now(), onupdate=datetime.now)]
str_uniq = Annotated[str, mapped_column(unique=True, nullable=False)]
str_null_true = Annotated[str, mapped_column(nullable=True)]

def init_db():
    Base.metadata.drop_all(engine)
    Base.metadata.create_all(engine)
    print('Init db has been success')
    

    

   


    
