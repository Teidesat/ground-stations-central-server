from ninja import Schema
from datetime import datetime

    
class UserSchema(Schema):
    username: str
    email: str = None
    first_name: str = None
    last_name: str = None

class UserError(Schema):
    message:str
    