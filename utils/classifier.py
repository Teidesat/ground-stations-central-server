from apps.analyze_image.task import run_tasks
from apps.analyze_image.models import Imagen
from .buffer import StackBuffer



class Classifier():
    def __init__(self):
        self.images = StackBuffer(maxsize=30)
        self.datos = StackBuffer(maxsize=30)

    async def identificar_tipo(self, type_data:str, data):
        type_data_cleaned = type_data.split('/')[0]
        data_format = type_data.split('/')[1]

        if type_data_cleaned == "image":
            img = await Imagen.objects.acreate(format=data_format, raw_data=data)
            self.images.add(img)
            imagen = self.images.get()
            await run_tasks(imagen)
        else:
            self.datos.add(data)

