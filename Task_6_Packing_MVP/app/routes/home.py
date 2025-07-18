from fastapi import APIRouter, Request, HTTPException, Response, Depends
from fastapi.templating import Jinja2Templates
from database.config import get_settings
from fastapi.responses import RedirectResponse
from schemas.user import SUserAuth, SUserRegister, SUser, SUserID, SUserInfo
from services.crud.usercrud import UsersCRUD
from services.auth.auth import AuthService


router = APIRouter(tags=['Личный кабинет'])

templates = Jinja2Templates(directory='templates')

settings = get_settings()


@router.get("/", summary='Страница приглашения в сервис!')
def home_page(request: Request):
    token = request.cookies.get(settings.COOKIE_NAME)
    if token:
        try:
            user = AuthService.get_user_from_token(token)
            panel = {'Пополнить баланс': ['Pay', 'fa-credit-card'], 
                     'Выход': ['Out', 'fa-sign-out-alt']
                     }
            try:
                admin = AuthService.get_current_admin_user(token)
                if admin:
                    panel = dict({'Функции администратора': ['Adm', 'fa-tasks'],},
                                **panel)
            except HTTPException as e:
                pass
                
            return templates.TemplateResponse(name='home.html',
                                              context={'request': request,
                                                       'user': user,
                                                       'panel': panel})
        except HTTPException:
            user = None
    
    return RedirectResponse("/login")

@router.get("/balance", summary='Пополнение баланса')
def balance_page(request: Request):
    token = request.cookies.get(settings.COOKIE_NAME)
    if token:
        try:
            user = AuthService.get_user_from_token(token)
            panel = {'Личный кабинет': ['ML', 'fa-brain ml-icon'], 
                     'Выход': ['Out', 'fa-sign-out-alt']
                     }
            
            try:
                admin = AuthService.get_current_admin_user(token)
                if admin:
                    panel = dict({'Функции администратора': ['Adm', 'fa-tasks'],},
                                 **panel)
            except HTTPException as e:
                pass
                        
            return templates.TemplateResponse(name='pay.html',
                                              context={'request': request,
                                                       'user': user,
                                                       'panel': panel})
        except HTTPException:
            user = None
    
    return RedirectResponse("/login")



@router.get("/admin", summary='Функции администратора!')
def admin_account(request: Request):
    token = request.cookies.get(settings.COOKIE_NAME)
    if token:
        try:
            user = AuthService.get_user_from_token(token)
            panel = {'Личный кабинет': ['ML', 'fa-brain ml-icon'],
                     'Пополнить баланс': ['Pay', 'fa-credit-card'], 
                     'Выход': ['Out', 'fa-sign-out-alt']
                     }
            
            table = list()
            for user_item in UsersCRUD.find_all_users():
                table.append({'id': user_item.id,
                               'email': user_item.email,
                               'balance': user_item.balance,
                               'loyalty': user_item.loyalty,
                               'admin': user_item.is_admin})
            
            try:
                admin = AuthService.get_current_admin_user(token)
            except HTTPException as e:
                RedirectResponse("/login")
                        
            return templates.TemplateResponse(name='adm.html',
                                              context={'request': request,
                                                       'user': user,
                                                       'panel': panel, 
                                                       'table': table})
        except HTTPException:
            user = None
    
    return RedirectResponse("/login")


@router.get("/registration", summary='Регистрация личного кабинета!')
def registration(request: Request):
    panel = {'Вход': ['In', 'fa-sign-in-alt']}
    return templates.TemplateResponse(name='registration.html', context={'request': request, 'panel': panel})


@router.get("/login", summary='Вход в личный кабинет!')
def login(request: Request):
    panel = {}
    return templates.TemplateResponse(name='auth.html', context={'request': request, 'panel': panel})


@router.get("/logout", summary='Покиинуть личный кабинет!')
def logout(response: Response, request: Request):
    response.delete_cookie(key=settings.COOKIE_NAME)
    return templates.TemplateResponse(name='auth.html', context={'request': request})


@router.get(
    "/image/{file}",
    responses = {
        200: {
            "content": {"image/png": {}}
        }
    },
    response_class=Response
)
def get_image(file: str, user: SUserInfo = Depends(AuthService.get_current_user)):
    with open(f'./files/{file}', 'rb') as f:
        image_bytes: bytes = f.read()
    return Response(content=image_bytes, media_type="image/png")
