from ninja import NinjaAPI, UploadedFile
import asyncio
from utils.classifier import Classifier
from utils.buffer import DataBuffer

api = NinjaAPI()
main_buffer = DataBuffer(maxsize=10)
classifier = Classifier()


api.add_router('/analyze-image', 'apps.analyze_image.api.router')


@api.post('/')
async def recibir_datos(request, files:list[UploadedFile]):
    for file in files:
        try:
            await main_buffer.add_data(data=file)
            data = await main_buffer.get_data()
            data_content = data.read()
            await classifier.identificar_tipo(data.content_type, data_content)
            print ('Todo ha funcionado')
        except:
            print('Todo mal')
