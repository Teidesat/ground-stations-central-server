from ninja import Schema
from datetime import datetime

class HelloSchema(Schema):
    name: str 
    
class UserSchema(Schema):
    username: str
    email: str = None
    first_name: str = None
    last_name: str = None

class UserError(Schema):
    message:str
    
    
class ImageSchema(Schema):
    id:int
    header:dict
    exif:dict

    