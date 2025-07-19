from fastapi import APIRouter, Response, HTTPException, status, Path, Depends, UploadFile, File, HTTPException
from typing import Annotated, List
from schemas.user import SUserAuth, SUserRegister, SUserInfo, SUserID
from schemas.packet import SUserGetPack, SPacketName, SPacketAdd
from schemas.events import SEvents
from services.auth.auth import AuthService
from services.crud.usercrud import UsersCRUD
from services.crud.packetscrud import PacketsCRUD
from services.crud.eventscrud import EventsCRUD
from io import BytesIO, StringIO
import pandas as pd

router = APIRouter(prefix='/users', tags=['Функции пользователя'])


@router.get('/user', summary='Информация о пользователе')
def getUser(user: SUserInfo = Depends(AuthService.get_current_user)) -> dict:
    
    result = {'id':user.id, 
              'email':user.email, 
              'last_name':user.last_name,
              'first_name':user.first_name}
    return result

@router.get('/user/packets', summary='Список пакетов пользователя, в каждом пакете несколько предсказаний')
def getPackets(user: SUserInfo = Depends(AuthService.get_current_user)) -> list:
    user_id = SUserGetPack(user_id = user.id)
    packets = PacketsCRUD.find_several(user_id)
    result = [{'id': itm.id, 
               'user_id': itm.user_id, 
               'uname': itm.uname, 
               'aname': itm.aname,
               'status': itm.status
               } for itm in packets]
    
    return result


@router.get('/user/events', summary='Список предсказаний пользователя')
def getEvents(user: SUserInfo = Depends(AuthService.get_current_user)) -> list:
    user_id = SUserGetPack(user_id = user.id)
    packets = PacketsCRUD.find_several_with_joined(user_id)
    result = [{'id': itm.id, 
               'user_id': itm.user_id, 
               'uname': itm.uname, 
               'aname': itm.aname,
               'status': itm.status,
               'events': [{c.name: getattr(e, c.name) for c in e.__table__.columns} for e in itm.events]
               } for itm in packets]
    
    return result

@router.post('/user/packet/add', summary='Добавить новый пакет')
def addPacket(data: SPacketName,user: SUserInfo = Depends(AuthService.get_current_user)) -> dict:
    item = SPacketAdd(user_id = user.id, aname=data.aname)
    packet = PacketsCRUD.add(item)
    result = {'id': packet.id, 
              'user_id': packet.user_id, 
              'uname': packet.uname, 
              'aname': packet.aname,
              'status': packet.status}
    
    return result

@router.post('/user/event/add', summary='Добавить новое строительное мероприятие')
def addEvent(data: SEvents, user: SUserInfo = Depends(AuthService.get_current_user)) -> dict:
    event = EventsCRUD.add(data)
    if event:
        record_dict = {c.name: getattr(event, c.name) for c in event.__table__.columns}
    
    return record_dict

@router.post('/user/event/batch/add', summary='Добавить несколько мероприятий')
def addEvents(data: List[SEvents], user: SUserInfo = Depends(AuthService.get_current_user)) -> list:
    records_dict = []

    for itm in data:
        event = EventsCRUD.add(itm)
    
        if event:
            records_dict.append({c.name: getattr(event, c.name) for c in event.__table__.columns})
    
    return records_dict

@router.post("user/event/upload/excel/")
async def uploadExcel(file: UploadFile = File(...), user: SUserInfo = Depends(AuthService.get_current_user)):

    if not file.filename.endswith(('.xlsx', '.xls')):
        raise HTTPException(
            status_code=400, 
            detail="Файл должен быть в формате Excel (.xlsx или .xls)"
        )
    
    try:
        records_dict = []
        contents = await file.read()
        excel_data = BytesIO(contents)
        df = pd.read_excel(excel_data)
        item = SPacketAdd(user_id = user.id, aname=file.filename)
        packet = PacketsCRUD.add(item)
        print('1')
        data_raw = df.to_dict(orient="records")
        data = []
        for raw_item in data_raw:
            new_item = {}
            for fld in ['year', 'type_of_work', 'contractor', 
                        'idleft', 'idright', 'g2', 'g3', 'g4', 'rrl', 'a_index', 
                        'a_region', 'a_place']:
                new_item[fld] = raw_item[fld]

            for fld in ['date_start', 'adr_prepare', 'tech_fin', 'equipment_fin', 
                                'equipment_prepared', 'contractor_accepted', 'ready_for_work',
                                'params_fin', 'integration_fin', 'monitoring_fin', 'commisioning_fin']:
                try:
                    if not raw_item[fld] is pd.NaT:
                        new_item[fld] = pd.Timestamp(raw_item[fld]).strftime("%Y-%m-%dT%H:%M:%S.%fZ")
                except Exception:
                    pass
            data.append(new_item)

        for itm in data:
            item = SEvents(**{'packet_id':packet.id, **itm})
            event = EventsCRUD.add(item)
            if event:
                records_dict.append({c.name: getattr(event, c.name) for c in event.__table__.columns})

        
        return records_dict
    
    except Exception as e:
        raise HTTPException(
            status_code=500, 
            detail=f"Ошибка при обработке файла: {str(e)}"
        )
    
    finally:
        await file.close()