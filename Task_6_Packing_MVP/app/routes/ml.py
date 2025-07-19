import uuid, base64, json, pandas as pd, base64
from fastapi import APIRouter, Response, HTTPException, status, File, Path, Form, Depends
from typing import Annotated, List
from services.auth.auth import AuthService
from services.crud.usercrud import UsersCRUD
from services.crud.eventscrud import EventsCRUD
from schemas.user import SUserID, SUserInfo
from schemas.events import SEvents, STarget
from schemas.packet import SPacketID, SPacketComplete
from services.rm.rm import RabbitMQSender
from io import StringIO





router = APIRouter(prefix='/ml', tags=['Обработка данных для модели машинного обучения'])

def user_checker(user_id: int = Form(...)):
   return user_id


@router.post("/predict", summary='Создать запрос на обработку пакета')
def predictk(packet_id: SPacketID, user: SUserInfo = Depends(AuthService.get_current_user)):
   
   batch_item = {'batchid': packet_id.packet_id}
   df = pd.DataFrame([{col.name: getattr(row, col.name) for col in row.__table__.columns} 
                      for row in EventsCRUD.find_several(packet_id)])
   #file_name = f'./files/{str(uuid.uuid4())}.csv'
   #df.to_csv(file_name, index=False, encoding='utf-8')
   csv_buffer = StringIO()
   df.to_csv(csv_buffer, index=False)
   csv_string = csv_buffer.getvalue()
   csv_bytes = csv_string.encode('utf-8')
   batch_item['bytes'] = base64.b64encode(csv_bytes).decode('ascii')
   #with open(file_name, 'rb') as f:
   #   csv = f.read()
   print(batch_item)

   with RabbitMQSender("ml_task_queue") as sender:
      print(sender.send_task(json.dumps(batch_item)))

   return {"status": "success"}


@router.patch("/task/complete", summary='Завершить ml задачу', include_in_schema=False)
def complete(task: SPacketComplete):
   decoded_bytes = base64.b64decode(task.result)  # base64 → bytes
   csv_string = decoded_bytes.decode('utf-8')
   df = pd.read_csv(StringIO(csv_string))
   print('look here')
   print(df.head())
   for item in df.itertuples():
      id = SPacketID(packet_id=item.Index)
      target = STarget(target=item[-2])
      EventsCRUD.update(id, target)