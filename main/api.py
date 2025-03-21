from django.contrib.auth.models import User
from ninja import NinjaAPI, UploadedFile, File
import asyncio
from .schemas import UserError, UserSchema, MsgSchema
from .buffer import DataBuffer
from .classifier import Classifier


api = NinjaAPI()
main_buffer = DataBuffer(maxsize=10)
classifier = Classifier()


api.add_router('/analyze-image', 'apps.analyze_image.api.router')



@api.get('/me', response={200: UserSchema, 403: UserError})
def me(request):
    if not request.user.is_authenticated:
        return 403, {'message': 'Please sign in first'}
    return request.user


@api.post('/createuser', response={200: UserSchema, 404: UserError})
def create_user(request, data: UserSchema):
    try:
        user = User.objects.create(
            username=data.username,
            email=data.email,
            first_name=data.first_name,
            last_name=data.last_name,
        )
        return user
    except:
        return 404, {'message': 'Te equivocaste en los campos'}

@api.post('/')
async def recibir_datos(request, file:UploadedFile = File(...)):
    try:
        await main_buffer.add_data(data=file)
        return 'Todo ha funcionado'
    except:
        return 'Todo mal'

@api.get('/datos')
def datos(request):
    try:
        data = asyncio.run(main_buffer.get_data())
        classifier.identificar_tipo(data.content_type, data)
        return "funciona"
    except:
        return "No hay datos"
    

@api.get('/prueba-clasificador')
def clasificador(request):
    try:
        print(classifier.images)
        print(classifier.datos)
        return 'funciona'
    except:
        return 'No funciona'