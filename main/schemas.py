from ninja import Schema


class UserSchema(Schema):
    username: str
    email: str = ''
    first_name: str = ''
    last_name: str = ''


class UserError(Schema):
    message: str
