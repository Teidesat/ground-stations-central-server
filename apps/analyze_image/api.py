import ast
import asyncio
from datetime import datetime
from io import BytesIO

import httpx
from django.http import HttpRequest
from ninja import File, Router, UploadedFile
from PIL import ExifTags, Image

from .models import Imagen
from .schemas import ImageSchema

router = Router()


@router.post(
    '/img',
)
def subir_imagen(request: HttpRequest, imagen: UploadedFile = File(...)):
    try:
        img = Image.open(imagen.file)
    except:
        return {'error': 'Archivo no es una imagen válida'}

    metadata = {
        'formato': img.format,
        'modo': img.mode,
        'tamaño': img.size,
    }

    output = BytesIO()
    img.convert('RGB').save(output, format='JPEG')

    exif_data = img.getexif()

    exif_dict = {}
    for tag_id, valor in exif_data.items():
        tag_nombre = ExifTags.TAGS.get(tag_id, tag_id)
        exif_dict[tag_nombre] = valor

    print(exif_dict)

    if 'DateTime' in exif_dict:
        date = datetime.strptime(exif_dict['DateTime'], '%Y:%m:%d %H:%M:%S')

        img = Imagen.objects.create(content=imagen, header=metadata, exif=exif_dict, fecha=date)

    # img = Imagen.objects.create(content=imagen, header=metadata, exif=exif_dict)

    return 'Ok'


@router.get('/listar_img', response=ImageSchema)
def listar_img(request):
    imagen = Imagen.objects.last()
    header = ast.literal_eval(imagen.header)
    exif = ast.literal_eval(imagen.exif)

    return {'id': imagen.id, 'header': header, 'exif': exif, 'fecha': imagen.fecha}


@router.get('/prueba-bufer')
def get_image(request):
    API_URL = 'http://127.0.0.1:8000/api/buffer/get'

    async def obtener_datos():
        async with httpx.AsyncClient() as client:
            response = await client.get(API_URL)
            return response.json()

    data = asyncio.run(obtener_datos())
    return data
