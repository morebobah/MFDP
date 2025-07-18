from fastapi import APIRouter, Response, HTTPException, status, Path, Depends
from schemas.user import SUserAuth, SUserRegister, SUser, SUserID
from typing import Annotated
from schemas.admin import SAdminID, SAdminEmail
from schemas.user import SUserInfo, SUserID
from services.auth.auth import AuthService
from services.crud.usercrud import UsersCRUD
from services.auth.auth import AuthService

router = APIRouter(prefix='/admin', tags=['Функции администратора'])

@router.get('/users', summary='Получить список пользователей')
def get_users(admin_data: SUserInfo = Depends(AuthService.get_current_admin_user)) -> list:
    result = list()
    for user in UsersCRUD.find_all_users():
        result.append({'id': user.id,
                      'email': user.email,
                      'first_name': user.first_name,
                      'last_name': user.last_name,
                      'balance': user.balance,
                      'loyalty': user.loyalty,
                      'is_admin': user.is_admin})
    return result


@router.get('/user/{user_id}', summary='Информация о пользователе')
def get_user(user_id: Annotated[int, Path(title='Идентификатор пользователя', gt=0)],
             admin_data: SUserInfo = Depends(AuthService.get_current_admin_user)) -> dict:

    user = UsersCRUD.find_one_or_none_by_id(id = user_id)
    if user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail='Пользователь не найден')
    result = {'id':user.id, 
              'email':user.email, 
              'last_name':user.last_name,
              'first_name':user.first_name, 
              'balance': user.balance, 
              'loyalty':user.loyalty}
    return result


@router.get('/balance/{user_id}', summary='Текущий баланс пользователя')
def get_balance(user_id: Annotated[int, Path(title='Идентификатор пользователя', gt=0)],
                admin_data: SUserInfo = Depends(AuthService.get_current_admin_user)) -> dict:

    user = UsersCRUD.find_one_or_none_by_id(SUserID(id = user_id))
    if user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail='Пользователь не найден')

    return {'message':'success', 'detail': 'Успешно', 'name': 'balance', 'value': user.balance}


@router.get('/loyalty/{user_id}', summary='Размер скидки пользователя по идентификатору')
def get_loyalty(user_id: Annotated[int, Path(title='Идентификатор пользователя', gt=0)], 
                admin_data: SUserInfo = Depends(AuthService.get_current_admin_user)) -> dict:

    user = UsersCRUD.find_one_or_none_by_id(id = user_id)
    if user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail='Пользователь не найден')

    return {'message':'success', 'detail': 'Успешно', 'name': 'loyalty', 'value': user.loyalty}


@router.post('/user', summary='Создать нового пользователя')
def create_users(user_data: SUserRegister, 
                 admin_data: SUserInfo = Depends(AuthService.get_current_admin_user)) -> dict:
    user_data.email = str.lower(user_data.email)
    user = UsersCRUD.find_one_or_none_by_email(SAdminEmail(email = user_data.email))
    if user:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail='Пользователь уже существует'
        )
    user_data.password = AuthService.get_password_hash(user_data.password)
    user = UsersCRUD.add(user_data)
    user = UsersCRUD.find_one_or_none_by_email(SAdminEmail(email = user_data.email))
    return {'detail': f'Новый пользователь зарегистрирован!',
            'id': user.id, 
            'email': user.email,
            'balance': user.balance,
            'admin': user.is_admin}


@router.put('/user/admin/id', summary='Предоставить права администратора по id')
def change_allow_admin_by_id(id: SAdminID,
                             admin_data: SUserInfo = Depends(AuthService.get_current_admin_user)) -> dict:
    user = UsersCRUD.find_one_or_none_by_id(id)
    if user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail='Пользователь не найден')
    UsersCRUD.allow_admin_by_id(id.id)
    return {'message': 'success', 'detail': 'Права администратора предоставлены'}


@router.delete('/user/admin/id', summary='Запретить права администратора по id')
def change_disallow_admin_by_id(id: SAdminID,
                                admin_data: SUserInfo = Depends(AuthService.get_current_admin_user)) -> dict:
    user = UsersCRUD.find_one_or_none_by_id(id)
    if user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail='Пользователь не найден')
    UsersCRUD.disallow_admin_by_id(id.id)
    return {'message': 'success', 'detail': 'Права администратора отозваны'}


@router.put('/user/admin/email', summary='Предоставить права администратора по email')
def change_allow_admin_by_email(email: SAdminEmail,
                                admin_data: SUserInfo = Depends(AuthService.get_current_admin_user)) -> dict:
    user = UsersCRUD.find_one_or_none_by_email(email = email)
    if user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail='Пользователь не найден')
    UsersCRUD.allow_admin_by_email(email)
    return {'message': 'success', 'detail': 'Права администратора предоставлены'}


@router.delete('/user/admin/email', summary='Запретить права администратора по email')
def change_disallow_admin_by_email(email: SAdminEmail,
                                   admin_data: SUserInfo = Depends(AuthService.get_current_admin_user)) -> dict:
    user = UsersCRUD.find_one_or_none_by_email(email = email)
    if user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail='Пользователь не найден')
    UsersCRUD.disallow_admin_by_email(email)
    return {'message': 'success', 'detail': 'Права администратора отозваны'}

