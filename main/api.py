from ninja import NinjaAPI, UploadedFile
from main.auth import SimpleTokenAuth
from utils.classifier import Classifier
from utils.buffer import StackBuffer
from utils.helpers import create_log
from main.tasks import run_control_while


api = NinjaAPI(auth=SimpleTokenAuth())
classifier = Classifier()
stack_buffer = StackBuffer(maxsize=150)

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

    )

    
    await run_control_while(stack_buffer, classifier)

    
    await create_log(
        level = 'INFO',
        logger = 'ground-stations-central-server',
        module = 'main',
        function= 'main.api',
        message= f'Finalizada la conexión con un total de {len(files)} archivos',
        request=request,
    )


@api.post('/RGS')
async def entry_rgs(request):
    pass