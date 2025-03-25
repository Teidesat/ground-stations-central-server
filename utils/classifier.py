
from apps.analyze_image.models import Imagen
from .buffer import DataBuffer


class Classifier():
    def __init__(self):
        self.images = DataBuffer()
        self.datos = DataBuffer()

    async def identificar_tipo(self, type_data:str, data):
        type_data_cleaned = type_data.split('/')[0]

        if type_data_cleaned == "image":
            print('se clasifica')
            img = await Imagen.objects.acreate(raw_data=data)
            
            self.images.add_data(img)
        else:
            self.datos.add_data(data)

