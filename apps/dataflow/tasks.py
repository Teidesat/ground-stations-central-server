import asyncio
import json
from asgiref.sync import sync_to_async
from utils.helpers import create_log


FIELDS= ['category', 'content', 'timestamp']


async def data_processing(data:object):
    try:
        raw_bytes = await sync_to_async(lambda: data.raw_data)()
        try:
            decoded = raw_bytes.decode('utf-8').strip()
        except UnicodeDecodeError as e:
            await create_log(
                level='ERROR',
                logger='ground-stations-central-server',
                module='data_processing',
                function='data_processing',
                message=f'No se pudo decodificar raw_data como UTF-8: {e}',
                exception=e,
            )
            return 

        decode_data = json.loads(decoded)

        if not all(field in decode_data for field in FIELDS):
            raise ValueError(f"Faltan campos obligatorios en el JSON: {decode_data}")

        data.category = decode_data['category']
        data.content = decode_data['content']
        data.timestamp = decode_data['timestamp']

        await sync_to_async(data.save)()

    except json.JSONDecodeError as e:
        await create_log(
            level='ERROR',
            logger='ground-stations-central-server',
            module='data_processing',
            function='data_processing',
            message=f'Error al decodificar JSON: {e}',
            exception=e,
        )

    except Exception as e:
        await create_log(
            level='ERROR',
            logger='ground-stations-central-server',
            module='data_processing',
            function='data_processing',
            message=f"Error inesperado en data_processing: {e}",
            exception=e,
        )


async def run_data_tasks(data:object):
   try:
        task = asyncio.create_task(data_processing(data))
        await task
   except Exception as e:
        await create_log(
            level='ERROR',
            logger='ground-stations-central-server',
            module='run_data_tasks',
            function='dataflow.tasks',
            message=f"Error al procesar data_obj en run_data_tasks: {e}",
            exception=e,
        )

