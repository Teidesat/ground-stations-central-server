import asyncio

async def control_while(buffer, classifier):
    while not buffer.is_empty():
        data = buffer.get()
        data_content = data.read()
        await classifier.identificar_tipo(data.content_type, data_content)


async def run_control_while(buffer, classifier):
    task = asyncio.create_task(control_while(buffer, classifier))
    await task