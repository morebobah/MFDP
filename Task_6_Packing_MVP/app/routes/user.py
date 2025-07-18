from fastapi import APIRouter, Response, HTTPException, status, Path, Depends
from typing import Annotated
from schemas.user import SUserAuth, SUserRegister, SUserInfo, SUserID
from services.auth.auth import AuthService
from services.crud.usercrud import UsersCRUD

router = APIRouter(prefix='/users', tags=['Функции пользователя'])


@router.get('/user', summary='Информация о пользователе')
def get_user(user: SUserInfo = Depends(AuthService.get_current_user)) -> dict:
    
    result = {'id':user.id, 
              'email':user.email, 
              'last_name':user.last_name,
              'first_name':user.first_name, 
              'balance': user.balance, 
              'loyalty':user.loyalty}
    return result


@router.get('/balance', summary='Текущий баланс пользователя')
def get_balance(user: SUserInfo = Depends(AuthService.get_current_user)) -> dict:

    return {'message':'success', 'detail': 'Успешно', 'name': 'balance', 'value': user.balance}


@router.get('/loyalty', summary='Размер скидки пользователя по идентификатору')
def get_loyalty(user: SUserInfo = Depends(AuthService.get_current_user)) -> dict:

    return {'message':'success', 'detail': 'Успешно', 'name': 'loyalty', 'value': user.loyalty}

