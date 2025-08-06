import uuid, base64, json, pandas as pd, base64, logging
from fastapi import APIRouter, Response, HTTPException, status, File, Path, Form, Depends
from typing import Annotated, List
from services.auth.auth import AuthService
from services.crud.usercrud import UsersCRUD
from services.crud.eventscrud import EventsCRUD
from services.crud.packetscrud import PacketsCRUD
from schemas.user import SUserID, SUserInfo
from schemas.events import SEvents, STarget, SEventID
from schemas.packet import SPacketID, SPacketComplete, SPacketStatus, SPacketPKID
from services.rm.rm import RabbitMQSender
from io import StringIO
from datetime import datetime

logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
) 

logger = logging.getLogger(__name__) 



router = APIRouter(prefix='/ml', tags=['Обработка данных для модели машинного обучения'])

def user_checker(user_id: int = Form(...)):
   return user_id


@router.post("/predict", summary='Создать запрос на обработку пакета')
def predict(packet_id: SPacketID, user: SUserInfo = Depends(AuthService.get_current_user)):
   
   batch_item = {'batchid': packet_id.packet_id}
   df = pd.DataFrame([{**{col.name: getattr(row, col.name) for col in row.__table__.columns}, **{'id': row.id}} 
                      for row in EventsCRUD.find_several(packet_id)])

   csv_buffer = StringIO()
   df.to_csv(csv_buffer, index=False)
   csv_string = csv_buffer.getvalue()
   csv_bytes = csv_string.encode('utf-8')
   batch_item['bytes'] = base64.b64encode(csv_bytes).decode('ascii')


   with RabbitMQSender("ml_task_queue") as sender:
      logger.info(sender.send_task(json.dumps(batch_item)))

   PacketsCRUD.update(SPacketPKID(id=packet_id.packet_id), SPacketStatus(status='pending'))
   

   return {"status": "success"}


@router.patch("/task/complete", summary='Завершить ml задачу', include_in_schema=False)
def complete(task: SPacketComplete):
   task_id = task.task_id
   data = json.loads(task.result)
   for item in data:
      id = SEventID(id=item['id'])
      target = STarget(target=datetime.fromtimestamp(item['target'][0] / 1000))
      EventsCRUD.update(id, target)

   PacketsCRUD.update(SPacketPKID(id=task_id), SPacketStatus(status='processed'))
