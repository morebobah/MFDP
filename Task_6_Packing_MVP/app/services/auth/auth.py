from fastapi import Request, HTTPException, status, Depends
from passlib.context import CryptContext
from jose import jwt, JWTError
from datetime import datetime, timedelta, timezone
from database.config import get_auth_data, get_settings
from services.crud.usercrud import UsersCRUD
from schemas.user import SUserAuth, SUserID, SUser, SUserEmail


pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
settings = get_settings()

def get_token(request: Request):
    token = request.cookies.get(settings.COOKIE_NAME)
    if not token:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Token not found')
    return token


class AuthService:

    @classmethod
    def get_password_hash(cls, password: str) -> str:
        return pwd_context.hash(password)


    @classmethod
    def verify_password(cls, plain_password: str, hashed_password: str) -> bool:
        return pwd_context.verify(plain_password, hashed_password)


    @classmethod
    def create_access_token(cls, data: dict) -> str:
        to_encode = data.copy()
        expire = datetime.now(timezone.utc) + timedelta(days=30)
        to_encode.update({"exp": expire})
        auth_data = get_auth_data()
        encode_jwt = jwt.encode(to_encode, auth_data['secret_key'], algorithm=auth_data['algorithm'])
        return encode_jwt


    @classmethod
    def authenticate_user(cls, auth_data: SUserAuth):
        user = UsersCRUD.find_one_or_none_by_email(SUserEmail(email=auth_data.email))
        if not user or cls.verify_password(plain_password=auth_data.password, hashed_password=user.password) is False:
            return None
        return user
    

    @classmethod
    def get_user_from_token(cls, token: str):
        try:
            auth_data = get_auth_data()
            payload = jwt.decode(token, auth_data['secret_key'], algorithms=[auth_data['algorithm']])
        except JWTError:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Invalid token')

        expire = payload.get('exp')
        expire_time = datetime.fromtimestamp(int(expire), tz=timezone.utc)
        if (not expire) or (expire_time < datetime.now(timezone.utc)):
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Token expiries')

        user_id = payload.get('sub')
        if not user_id:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='User not found')
        

        user = UsersCRUD.find_one_or_none_by_id(SUserID(id=user_id))
        if not user:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='User not found')

        return user

  
    @classmethod
    def get_current_user(cls, token: str = Depends(get_token)):
        return cls.get_user_from_token(token)


    @classmethod
    def get_current_admin_user(cls, token: str = Depends(get_token)):
        current_user = cls.get_user_from_token(token)
        if current_user.is_admin:
            return current_user
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail='Недостаточно прав!')