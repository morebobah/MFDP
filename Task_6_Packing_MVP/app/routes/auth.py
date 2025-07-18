from fastapi import APIRouter, Response, HTTPException, status
from database.config import get_settings
from schemas.user import SUserAuth, SUserRegister, SUser, SUserID, SUserEmail
from services.auth.auth import AuthService
from services.crud.usercrud import UsersCRUD


router = APIRouter(prefix='/auth', tags=['Авторизация пользователя'])
settings = get_settings()



@router.post('/register', summary='Регистрация нового пользователя')
def register_user(response: Response, user_data: SUserRegister) -> dict:
    user_data.email = str.lower(user_data.email)
    user_email = SUserEmail(email = user_data.email)
    user = UsersCRUD.find_one_or_none_by_email(user_email)
    if user:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail='Пользователь уже существует'
        )
    password = user_data.password
    user_data.password = AuthService.get_password_hash(password=password)
    UsersCRUD.add(user_data)

    user_data = SUserAuth(email=user_data.email, password=password)
    check = AuthService.authenticate_user(user_data)
    if check is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail='Неверное имя пользователя или пароль')
    
    access_token = AuthService.create_access_token({"sub": str(check.id)})
    response.set_cookie(key=settings.COOKIE_NAME, value=access_token, httponly=True)

    return {'message': 'success', 'detail': 'Вы успешно зарегистрированы!'}


@router.post("/login", summary='Авторизация пользователя')
def login_user(response: Response, user_data: SUserAuth):
    check = AuthService.authenticate_user(user_data)
    if check is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail='Неверное имя пользователя или пароль')
    
    access_token = AuthService.create_access_token({"sub": str(check.id)})
    response.set_cookie(key=settings.COOKIE_NAME, value=access_token, httponly=True)

    return {'message': 'success', 'detail': 'Успешная авторизация'}



@router.get("/logout", summary='Выход из личного кабинета')
def logout_user(response: Response):
    response.delete_cookie(key=settings.COOKIE_NAME)
    return {'message': 'success', 'detail': 'Успешный выход'}

