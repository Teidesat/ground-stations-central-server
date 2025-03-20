from ninja import Router

from .buffer import DataBuffer
from .schema import DataSchema

router = Router()

buffer = DataBuffer(maxsize=10)


@router.post('/add')
async def add_data(request, data: DataSchema):
    await buffer.add_data(data)
    return {'message': 'Dato agregado al buffer'}


@router.get('/get')
async def get_data(request):
    data = await buffer.get_data()
    buffer.task_done()
    return {'message': 'Dato procesado', 'data': data}
