import asyncio
import json
from asgiref.sync import sync_to_async
from utils.helpers import create_log


FIELDS= ['category', 'content', 'timestamp']


async def data_proccesing(data:object):
    try:
        decode_data = data.raw_data.decode('utf-8').strip()
        decode_data = json.loads(decode_data)

        data.category = decode_data['category']
        data.content = decode_data['content']
        data.timestamp = decode_data['timestamp']

        await sync_to_async(data.save)()
    
    except json.JSONDecodeError as e:
        await create_log(
            level = 'ERROR',
            logger = 'ground-stations-central-server',
            module = 'data_proccesing',
            function= 'dataflow.tasks',
            message= f'Error al decodificar JSON: {e}'
        )
    
    except Exception as e:
        await create_log(
            level = 'ERROR',
            logger = 'ground-stations-central-server',
            module = 'data_proccesing',
            function= 'dataflow.tasks',
            message= f"Error inesperado en data_proccesing: {e}"
        )

async def run_data_tasks(data:object):
    task = asyncio.create_task(data_proccesing(data))
    await task
