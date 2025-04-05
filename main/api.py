from ninja import NinjaAPI, UploadedFile
from main.auth import SimpleTokenAuth
from utils.classifier import Classifier
from utils.buffer import StackBuffer

api = NinjaAPI(auth=SimpleTokenAuth())
classifier = Classifier()
stack_buffer = StackBuffer(maxsize=60)

api.add_router('/analyze-image', 'apps.analyze_image.api.router')
api.add_router('/dataflow', 'apps.dataflow.api.router')
api.add_router('/logvault', 'apps.logvault.api.router')



@api.post('/')
async def recibir_datos(request, files:list[UploadedFile]):
    for file in files:
        stack_buffer.add(file)

    while not stack_buffer.is_empty():
        data = stack_buffer.get()
        data_content = data.read()
        await classifier.identificar_tipo(data.content_type, data_content)