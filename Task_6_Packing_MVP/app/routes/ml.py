import uuid, base64, json, pandas as pd, base64
from fastapi import APIRouter, Response, HTTPException, status, File, Path, Form, Depends
from typing import Annotated, List
from services.auth.auth import AuthService
from services.crud.usercrud import UsersCRUD
from services.crud.workscrud import WorksCRUD
from schemas.user import SUserID, SUserInfo
from schemas.works import SWorks, SWorksPacket, STaskComplete, SWorkID, STarget
from services.rm.rm import RabbitMQSender
from io import StringIO





router = APIRouter(prefix='/ml', tags=['Загрузка данных для модели машинного обучения'])

def user_checker(user_id: int = Form(...)):
   return user_id


@router.post("/one", summary='Создать запрос на обработку пакета')
def upload_task(data: SWorks,
                user: SUserInfo = Depends(AuthService.get_current_user)):
   WorksCRUD.add(data)
   return {"status": "success"}


@router.post("/batch", summary='Создать запрос на обработку пакета')
def upload_task(data: List[SWorks],
                user: SUserInfo = Depends(AuthService.get_current_user)):
   batchid = SWorksPacket(packet=data[0].packet)

   for row in data:
      WorksCRUD.add(row)
   
   df = pd.DataFrame([{col.name: getattr(row, col.name) for col in row.__table__.columns} 
                      for row in WorksCRUD.find_several(batchid)])
   file_name = f'./files/{str(uuid.uuid4())}.csv'
   df.to_csv(file_name, index=False, encoding='utf-8')
   with open(file_name, 'rb') as f:
      csv = f.read()


   batch_item = {'batchid': batchid.packet,
                 'batch_file': file_name}
   batch_item['bytes'] = base64.b64encode(csv).decode('ascii')
   with RabbitMQSender("ml_task_queue") as sender:
      print(sender.send_task(json.dumps(batch_item)))

   return {"status": "success"}

@router.patch("/task/complete", summary='Завершить ml задачу', include_in_schema=False)
def complete(task: STaskComplete):
   decoded_bytes = base64.b64decode(task.result)  # base64 → bytes
   csv_string = decoded_bytes.decode('utf-8')
   df = pd.read_csv(StringIO(csv_string))
   print('look here')
   print(df.head())
   for item in df.itertuples():
      id = SWorkID(id=item.Index)
      target = STarget(target=item[-2])
      WorksCRUD.update(id, target)