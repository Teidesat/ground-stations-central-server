from ninja import Schema

class ImageSchema(Schema):
    id:int
    header:dict
    exif:dict
