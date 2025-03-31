import io
from PIL import Image
import asyncio
from django.core.files.uploadedfile import InMemoryUploadedFile
from asgiref.sync import sync_to_async
from utils.helpers import create_log

async def image_proccesing(img:object):
    try:
        img_bytes = io.BytesIO(img.raw_data)
        imagen = Image.open(img_bytes)
        img_buffer = io.BytesIO()
        imagen.save(img_buffer, format=img.format)
        img_buffer.seek(0)  

        image_file = InMemoryUploadedFile(
            img_buffer,
            field_name=None,  
            name="image.png",  
            content_type="image/png",  
            size=len(img_buffer.getvalue()),  
            charset=None
        )

        img.content = image_file
        await sync_to_async(img.save)()
    
    except Exception as e:
        await create_log(
            level= 'ERROR',
            logger='ground-stations-central-server',
            module='analyze_image.tasks',
            function='image_proccesing',
            message= f'ERROR en el procesamiento de la imagen: {e}'
        )

async def run_tasks(img:object):
   task = asyncio.create_task(image_proccesing(img))
   await task
 

