from ninja import NinjaAPI, UploadedFile
from main.auth import SimpleTokenAuth
from utils.classifier import Classifier
from utils.buffer import StackBuffer
from utils.helpers import create_log

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

    await create_log(
        level = 'INFO',
        logger = 'ground-stations-central-server',
        module = 'main',
        function= 'main.api',
        message= f'Iniciada la conexión con un total de {len(files)} archivos',
        request=request,
        request_status_code=200,
    )


    while not stack_buffer.is_empty():
        data = stack_buffer.get()
        data_content = data.read()
        await classifier.identificar_tipo(data.content_type, data_content)
    
    await create_log(
        level = 'INFO',
        logger = 'ground-stations-central-server',
        module = 'main',
        function= 'main.api',
        message= f'Finalizada la conexión con un total de {len(files)} archivos',
        request=request,
        request_status_code=200,
    )


@api.post('/RGS')
async def entry_rgs(request):
    pass