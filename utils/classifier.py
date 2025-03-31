from apps.analyze_image.task import run_tasks
from apps.dataflow.tasks import run_data_tasks
from apps.analyze_image.models import Imagen
from apps.dataflow.models import SatelliteData
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
        elif type_data_cleaned == 'application' and data_format == 'octet-stream':
            data_raw =  await SatelliteData.objects.acreate(raw_data=data) 
            self.datos.add(data_raw)
            data_obj = self.datos.get()
            await run_data_tasks(data_obj)
        else:
            print('Esto no es un binario')

