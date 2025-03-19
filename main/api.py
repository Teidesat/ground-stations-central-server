from ninja import NinjaAPI
from .schemas import HelloSchema, UserSchema, UserError
from django.contrib.auth.models import User

api = NinjaAPI()

api.add_router('/prueba', "prueba.api.router")



@api.get('/')
def home(request):
    return "estoy en el home"

@api.post("/hello", url_name="hello")
def hello(request, data: HelloSchema):
    return f'Hello {data.name}'


@api.get('/me', response={200: UserSchema, 403: UserError})
def me(request):
    if not request.user.is_authenticated:
        return 403, {"message": "Please sign in first"}
    return request.user

@api.post('/createuser', response={200:UserSchema, 404: UserError})
def create_user(request, data:UserSchema):
    try:
        user = User.objects.create(
            username= data.username,
            email= data.email,
            first_name= data.first_name,
            last_name= data.last_name,
        )
        return user
    except:
        return 404, {"message": "Te equivocaste en los campos"}