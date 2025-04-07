import asyncio
from utils.helpers import create_log


async def control_while(buffer, classifier):
    while not buffer.is_empty():
        try:
            data = buffer.get()
            data_content = data.read()
            await classifier.identificar_tipo(data.content_type, data_content)
        except Exception as e:
            await create_log(
                level='ERROR',
                logger='ground-stations-central-server',
                module='control_while',
                function='main_loop',
                message=f'Fallo en el procesamiento del buffer: {e}',
                exception=e,
            )

async def run_control_while(buffer, classifier):
    task = asyncio.create_task(control_while(buffer, classifier))
    await task