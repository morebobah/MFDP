import os, pandas as pd, numpy as np, joblib, xgboost as xgb, pika, logging, json, time, base64
from datetime import timedelta
import httpx
from io import StringIO

logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
) 

logger = logging.getLogger(__name__) 

connection_params = pika.ConnectionParameters(host='rabbitmq',
                                              port=5672,
                                              virtual_host='/',
                                              credentials=pika.PlainCredentials(
                                                  username='rbbmq',
                                                  password='rbbmqpwd'
                                              ),
                                              heartbeat=30,
                                              blocked_connection_timeout=2)

connection = pika.BlockingConnection(connection_params)

channel = connection.channel()
queue_name = 'ml_task_queue'
channel.queue_declare(queue=queue_name)


url = 'https://raw.githubusercontent.com/morebobah/MFDP/refs/heads/main/Task_5_Improving_The_Model/best_params.csv'
df_params = pd.read_csv(url, index_col=0)
xgb_models_best = {idx: None for idx in df_params.index}
keys = xgb_models_best.keys()
for model in [model for model in os.listdir() if model.endswith('.pkl')]:
    if model[10:-4] in keys:
        xgb_models_best[model[10:-4]] = joblib.load(model)

def convertDate(date = '2000-11-05 18:35:11.2'):
    result = pd.Timestamp('1970-01-01')
    try:
        result = pd.to_datetime(date, format='%Y-%m-%d %H:%M:%S.%f')

    except ValueError:

            try:
                result = pd.to_datetime(date, format='%Y-%m-%d %H:%M:%S')

            except ValueError:
                result = pd.to_datetime(date, format='%Y-%m-%d') + timedelta(seconds=1)

    return result

def predict_delta(df_origin):
    features = 12
    fields = ['year', 'type_of_work', 'contractor', 'idleft', 'idright', 
          '2g', '3g', '4g', 'rrl', 'a_index', 'a_region', 'a_place', #*weather, *contractor_weather, 
          'delta_start', 'delta_tech', 'delta_spe', 'delta_contractor', 
          'delta_equipment', 'delta_ready', 'delta_params', 'delta_integration',
          'delta_monitoring', 'delta_commisioning']
    weather_fields = ['date_start', 'ADR_PREPARE', 'tech_fin', 'equipment_fin', 'EQUIPMENT_PREPARED', 'CONTRACTOR_ACCEPTED', 'READY_FOR_WORK', 'params_fin', 'integration_fin', 'monitoring_fin', 'commisioning_fin']

    contractor_weather = []
    for idx, wea in enumerate(weather_fields):
        contractor_weather.append(f'cw{idx}')
    
    #df_origin = pd.read_csv(csv_path, index_col=0)
    df = df_origin.rename(columns={'g2': '2g', 'g3': '3g','g4': '4g'})
    data_fields = ['date_start', 'adr_prepare', 'tech_fin', 'equipment_fin', 'equipment_prepared', 'contractor_accepted',
                   'ready_for_work', 'params_fin', 'integration_fin', 'monitoring_fin', 'commisioning_fin']
    
    for f in data_fields:
        df[f] = convertDate(df[f])

    df['delta_start'] = (df['adr_prepare'] - df['date_start'])/timedelta(days=1) #Время от добавления в систему до начала работ
    df['delta_tech'] = (df['tech_fin'] - df['adr_prepare'])/timedelta(days=1) #Время от начала работ до готовности технической части
    df['delta_spe'] = (df['equipment_fin'] - df['tech_fin'])/timedelta(days=1) #Время от готовности технической части до заказа оборудования
    df['delta_equipment'] = (df['equipment_prepared'] - df['equipment_fin'])/timedelta(days=1) #Время от начала работ до комплектации
    df['delta_contractor'] = (df['contractor_accepted'] - df['tech_fin'])/timedelta(days=1) #Время от готовности технической части до проектирования
    df['delta_ready'] = (df['ready_for_work'] - df['equipment_prepared'])/timedelta(days=1) #Время от комплектации до готовности к пуску
    df['delta_params'] = (df['params_fin'] - df['ready_for_work'])/timedelta(days=1) #Время от готовности к пуску до готовности параметров
    df['delta_integration'] = (df['integration_fin'] - df['params_fin'])/timedelta(days=1) #Время от готовности к пуску до интеграции
    df['delta_monitoring'] = (df['monitoring_fin'] - df['integration_fin'])/timedelta(days=1) #Время от готовности к пуску до интеграции
    df['delta_commisioning'] = (df['commisioning_fin'] - df['monitoring_fin'])/timedelta(days=1) #Время от готовности к пуску до интеграции
    weather_fields = ['date_start', 'adr_prepare', 'tech_fin', 'equipment_fin', 'equipment_prepared', 'contractor_accepted', 'ready_for_work', 'params_fin', 'integration_fin', 'monitoring_fin', 'commisioning_fin']
    weather = []
    for idx, wea in enumerate(weather_fields):
        df[f'weather{idx}'] = pd.to_datetime(df[wea], format='%Y-%m-%d').dt.month
        weather.append(f'weather{idx}')
    
    contractor_weather = []
    for idx, wea in enumerate(weather_fields):
        df[f'cw{idx}'] = df['contractor'] * 100 + df[f'weather{idx}']
        contractor_weather.append(f'cw{idx}')
    
    df_leftout = df.copy(deep=True)
    df = df_leftout[fields]
    actual_fields = []
    for fld in fields:
        if not df[fld].isna().any():
            actual_fields.append(fld)
    
    for x in df.columns:
        logger.info(f'{x} {df[x]}')
    
    df = df[actual_fields]
    result = len(actual_fields) - 1

    #logger.info('look here')
    #logger.info(result)
    #logger.info(f'model {fields[result]}')
    #logger.info(fields[:result + 1])
    #logger.info(fields[:result  + 1] + weather[:result-features+1])
    #logger.info(fields[:result  + 1] + weather[:result-features+1] + contractor_weather[:result-features+1])
    #logger.info(df_leftout[:result  + 1].columns)
    #logger.info(xgb_models_best)
    
    try:
        X = df[:result  + 1]
        dtest = xgb.DMatrix(X)
        y_pred = xgb_models_best[fields[result]].predict(dtest)
    except ValueError:
        try:
            X = df[fields[:result  + 1] + weather[:result-features+1]]
            dtest = xgb.DMatrix(X)
            y_pred = xgb_models_best[fields[result]].predict(dtest)
        except ValueError:
            X = df[fields[:result  + 1] + weather[:result-features+1] + contractor_weather[:result-features+1]]
            dtest = xgb.DMatrix(X)
            y_pred = xgb_models_best[fields[result]].predict(dtest)
    
    logger.info(y_pred)
    logger.info('free')
    df_origin['delta_all'] = y_pred
    df_origin['date_start'] = convertDate(df_origin['date_start'])
    df_origin['target'] = df_origin['date_start'] + pd.to_timedelta(df_origin['delta_all'], unit='D')

    return df_origin['target']
    
def callback(ch, method, properties, body, *args, **kwargs):
    payload = json.loads(body)

    df_origin = pd.read_csv( StringIO(base64.b64decode(payload['bytes']).decode('utf-8') ))
    logger.info('look here')
    logger.info(df_origin.columns)

    deltas = []
    for index, row in df_origin.iterrows():
        # Создаем DataFrame из одной строки
        row_df = pd.DataFrame([row])
        delta = predict_delta(row_df)
        deltas.append(delta)
    logger.info('smooth')
    logger.info(deltas)
    logger.info('target before')
    logger.info(df_origin['target'])
    df_origin['target'] = deltas
    logger.info('target after')
    logger.info(df_origin['target'])
    #df_origin['target'] = df_origin.apply(predict_delta, axis=1)
    #df = predict_delta(df_origin)
    #os.remove(file_name)
    
    

    result_item = {'task_id': '0', 'status': 'success'}
    #csv_buffer = StringIO()
    #df_origin.to_csv(csv_buffer, index=False)  # index=False, чтобы не сохранять индексы
    #csv_string = csv_buffer.getvalue()
    #csv_bytes = csv_string.encode('utf-8')  # str → bytes
    #base64_bytes = base64.b64encode(csv_bytes)  # bytes → base64 bytes
    #result_item['result'] = base64_bytes.decode('ascii')
    result_item['result'] = df_origin[['id', 'target']].to_json(orient='records')
    json_data = json.dumps(result_item)
    logger.info(result_item['result'])

    
    #data = {'task_id': payload['task_id'],
    #        'user_id': payload['user_id'],
    #        'result': result, 
    #        'cost': model_cost, 
    #        'key': 'secret_key'}
    
    r = httpx.patch('http://app:8000/ml/task/complete', 
                   data=json_data, 
                   headers={"Content-Type": "application/json"},)
    if 199<r.status_code<300:
        logger.info(f'Успешно: "{r.json()}"')
    else:
        logger.info(f'С ошибкой: "{r.json()}"')
    
    ch.basic_ack(delivery_tag=method.delivery_tag)
    
    

channel.basic_consume(queue_name, 
                     on_message_callback=callback,
                     auto_ack=False)

logger.info('Waiting for messages. To exit, press Ctrl+C') 
channel.start_consuming()