from fastapi import FastAPI
from routes.home import router as home_router
from routes.auth import router as auth_router
from routes.user import router as user_router
from routes.ml import router as ml_router
from routes.admin import router as admin_router
from routes.health import router as health_router
from database.database import init_db
from services.crud.usercrud import UsersCRUD
from schemas.user import SUser, SUserEmail
from services.auth.auth import AuthService
import uvicorn



def lifespan(app: FastAPI):
    init_db()
    
    user = SUser(first_name='User', 
                 last_name='Test', 
                 email='user@test.ru', 
                 password=AuthService.get_password_hash('testpwd'),
                 is_access=True,
                 is_admin=False, 
                )
    
    if UsersCRUD.find_one_or_none_by_email(SUserEmail(email=user.email)) is None:
        UsersCRUD.add(user)


    admin = SUser(first_name='Administrator', 
                 last_name='Superuser', 
                 email='admin@test.ru', 
                 password=AuthService.get_password_hash('testadminpwd'),
                 is_access=True,
                 is_admin=True)
    
    if UsersCRUD.find_one_or_none_by_email(SUserEmail(email=admin.email)) is None:
        UsersCRUD.add(admin)
    
    yield



app = FastAPI(lifespan=lifespan)


app.include_router(health_router)
app.include_router(home_router)
app.include_router(auth_router)
app.include_router(user_router)
app.include_router(ml_router)
#app.include_router(admin_router)




if __name__=='__main__':
    uvicorn.run('api:app', host='0.0.0.0', port=8000, reload=True)