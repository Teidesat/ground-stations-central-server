from ninja import Router, Query
from django.http import JsonResponse

from apps.core.models import TelemetryMessage, CommandMessage, EventMessage, StatusMessage 
from .schemas import *
from .services import send_data, get_data, store_command_data, store_event_data, store_status_data, store_telemetry_data

from apps.logvault.services import create_log
from main.settings import RGS_URL, OGS_URL, FOMALHAUT_URL

router = Router()

# RUTAS HISTORICAS (BD)

# Rutas para telemetría historica
# GET
@router.get('/historical/telemetry', response=list[TelemetryMessageSchema])
async def get_telemetry_data(request, filters: TelemetryFilterSchema = Query(...)):
    qs = TelemetryMessage.objects.all()
    qs = filters.filter(qs)
    exists = await qs.aexists()

    if not exists:
        await create_log(
            level= 'WARNING',
            logger='ground-stations-central-server',
            module='dataflow.api',
            function='get_telemetry_data',
            message= f'No hay datos de telemetría disponibles que coincidan con los filtros proporcionados',
            request=request
        )
        return JsonResponse({'error': 'No telemetry data found with the provided filters'}, status=404)

    await create_log(
        level= 'INFO',
        logger='ground-stations-central-server',
        module='dataflow.api',
        function='get_telemetry_data',
        message= f'Petición de datos de telemetría realizada',
        request=request
    )

    results = [item async for item in qs]

    return results

# Ruta obtención de eventos historicos
# GET
@router.get('/historical/events', response=list[EventMessageSchema])
async def get_event_data(request, filters: EventFilterSchema = Query(...)):
    qs = EventMessage.objects.all()
    qs = filters.filter(qs)
    exists = await qs.aexists()

    if not exists:
        await create_log(
            level= 'WARNING',
            logger='ground-stations-central-server',
            module='dataflow.api',
            function='get_event_data',
            message= f'No hay datos de eventos disponibles que coincidan con los filtros proporcionados',
            request=request
        )
        return JsonResponse({'error': 'No event data found with the provided filters'}, status=404)

    await create_log(
        level= 'INFO',
        logger='ground-stations-central-server',
        module='dataflow.api',
        function='get_event_data',
        message= f'Petición de datos de eventos realizada',
        request=request
    )

    results = [item async for item in qs]

    return results


# Ruta para obtener status historico
# GET
@router.get('/historical/status', response=list[StatusMessageSchema])
async def get_status_data(request, filters: StatusFilterSchema = Query(...)):
    qs = StatusMessage.objects.all()
    qs = filters.filter(qs)
    exists = await qs.aexists()

    if not exists:
        await create_log(
            level= 'WARNING',
            logger='ground-stations-central-server',
            module='dataflow.api',
            function='get_status_data',
            message= f'No hay datos de estado del sistema disponibles que coincidan con los filtros proporcionados',
            request=request
        )
        return JsonResponse({'error': 'No status data found with the provided filters'}, status=404)
    
    await create_log(
        level= 'INFO',
        logger='ground-stations-central-server',
        module='dataflow.api',
        function='get_status_data',
        message= f'Petición de datos de estado del sistema realizada',
        request=request
    )

    results = [item async for item in qs]
    
    return results

# Ruta para otener comandos historicos
# GET
@router.get('/historical/commands', response=list[CommandMessageSchema])
async def get_command_data(request, filters: CommandFilterSchema = Query(...)):
    qs = CommandMessage.objects.all()
    qs = filters.filter(qs)
    exists = await qs.aexists()

    if not exists:
        await create_log(
            level= 'WARNING',
            logger='ground-stations-central-server',
            module='dataflow.api',
            function='get_command_data',
            message= f'No hay datos de comandos disponibles',
            request=request
        )
        return JsonResponse({'error': 'No command data found with the provided filters'}, status=404)

    await create_log(
        level= 'INFO',
        logger='ground-stations-central-server',
        module='dataflow.api',
        function='get_command_data',
        message= f'Petición de datos de comandos realizada',
        request=request
    )

    results = [item async for item in qs]

    return results

# RUTAS TIEMPO REAL

# Ruta para envio de comandos
# POST
@router.post('/stream/commands')
async def send_command_data(request, data: CommandMessageSchema):
    try:
        await create_log(
            level= 'INFO',
            logger='ground-stations-central-server',
            module='dataflow.api',
            function='send_command_data',
            message= f'Enviando comando',
            request=request
        )

        url = ""

        if data.destination == "satellite":
            url = RGS_URL + '/commands'
        elif data.destination == "radio_station":
            url = RGS_URL + '/commands'
        elif data.destination == "optical_station":
            url = OGS_URL + '/commands'
        elif data.destination == "fomalhaut":
            url = FOMALHAUT_URL + '/commands'
        else:
            return JsonResponse({'error': 'Invalid command destination'}, status=400)

        response: CommandMessageSchema = await send_data(
            url, 
            data.dict()
        )

        await create_log(
            level= 'INFO',
            logger='ground-stations-central-server',
            module='dataflow.api',
            function='send_command_data',
            message= f'Comando enviado correctamente',
            request=request
        )

        await store_command_data(data)

        await store_command_data(response)

        return JsonResponse({
            'status': 'success',
            'message': response
        },  status=200)

    except Exception as e:
        await create_log(
            level= 'ERROR',
            logger='ground-stations-central-server',
            module='dataflow.api',
            function='send_command_data',
            message= f'ERROR en la solicitud de envío de comando: {e}',
            request=request,
            exception=e,
        )
        return JsonResponse({'error': 'Failed to send command'}, status=502)
    

# Ruta para obtención telemetria en tiempo real
@router.get('/stream/telemetry')
async def get_live_telemetry(request, params: TelemetryRequestSchema = Query(...)):
    try:
        await create_log(
            level= 'INFO',
            logger='ground-stations-central-server',
            module='dataflow.api',
            function='get_live_telemetry',
            message= f'Obteniendo datos de telemetría en tiempo real',
            request=request
        )
        
        url = ""

        if params.destination == "satellite":
            url = RGS_URL + '/telemetry'
        elif params.destination == "radio_station":
            url = RGS_URL + '/telemetry'
        elif params.destination == "optical_station":
            url = OGS_URL + '/telemetry'
        elif params.destination == "fomalhaut":
            url = FOMALHAUT_URL + '/telemetry'
        else:
            return JsonResponse({'error': 'Invalid command destination'}, status=400)
        
        response: TelemetryMessageSchema = await get_data(
            url,
            params.dict()
        )

        create_log(
            level= 'INFO',
            logger='ground-stations-central-server',
            module='dataflow.api',
            function='get_live_telemetry',
            message= f'Datos de telemetría en tiempo real obtenidos correctamente',
            request=request
        )

        await store_telemetry_data(response)

        return JsonResponse({
            'status': 'success',
            'message': response
        },  status=200)
        

    except Exception as e:
        await create_log(
            level= 'ERROR',
            logger='ground-stations-central-server',
            module='dataflow.api',
            function='get_live_telemetry',
            message= f'ERROR al obtener datos de telemetría en tiempo real: {e}',
            request=request,
            exception=e,
        )
        return JsonResponse({'error': 'Failed to fetch live telemetry data'}, status=502)

# Ruta para obtención eventos en tiempo real
@router.get('/stream/events')
async def get_live_events(request, params: EventRequestSchema = Query(...)):
    try:
        await create_log(
            level= 'INFO',
            logger='ground-stations-central-server',
            module='dataflow.api',
            function='get_live_events',
            message= f'Obteniendo datos de eventos en tiempo real',
            request=request
        )

        url = ""

        if params.destination == "satellite":
            url = RGS_URL + '/events'
        elif params.destination == "radio_station":
            url = RGS_URL + '/events'
        elif params.destination == "optical_station":
            url = OGS_URL + '/events'
        elif params.destination == "fomalhaut":
            url = FOMALHAUT_URL + '/events'
        else:
            return JsonResponse({'error': 'Invalid command destination'}, status=400)
        
        response: EventMessageSchema = await get_data(
            url,
            params.dict()
        )

        await create_log(
            level= 'INFO',
            logger='ground-stations-central-server',
            module='dataflow.api',
            function='get_live_events',
            message= f'Datos de eventos en tiempo real obtenidos correctamente',
            request=request
        )

        await store_event_data(response)
        
        return JsonResponse({
            'status': 'success',
            'message': response
        },  status=200)
        
    except Exception as e:
        await create_log(
            level= 'ERROR',
            logger='ground-stations-central-server',
            module='dataflow.api',
            function='get_live_events',
            message= f'ERROR al obtener datos de eventos en tiempo real: {e}',
            request=request,
            exception=e,
        )
        return JsonResponse({'error': 'Failed to fetch live event data'}, status=502)



# Ruta para obtener status en tiempo real
@router.get('/stream/status')
async def get_live_status(request, params: StatusRequestSchema = Query(...)):
    try:
        await create_log(
            level= 'INFO',
            logger='ground-stations-central-server',
            module='dataflow.api',
            function='get_live_status',
            message= f'Obteniendo datos de estado del sistema en tiempo real',
            request=request
        )

        url = ""

        if params.destination == "satellite":
            url = RGS_URL + '/status'
        elif params.destination == "radio_station":
            url = RGS_URL + '/status'
        elif params.destination == "optical_station":
            url = OGS_URL + '/status'
        elif params.destination == "fomalhaut":
            url = FOMALHAUT_URL + '/status'
        else:
            return JsonResponse({'error': 'Invalid command destination'}, status=400)
        
        response: StatusMessageSchema = await get_data(
            url,
            params.dict()
        )

        await create_log(
            level= 'INFO',
            logger='ground-stations-central-server',
            module='dataflow.api',
            function='get_live_status',
            message= f'Datos de estado del sistema en tiempo real obtenidos correctamente',
            request=request
        )

        await store_status_data(response)

        return JsonResponse({
            'status': 'success',
            'message': response
        },  status=200)
    
    except Exception as e:
        await create_log(
            level= 'ERROR',
            logger='ground-stations-central-server',
            module='dataflow.api',
            function='get_live_status',
            message= f'ERROR al obtener datos de estado del sistema en tiempo real: {e}',
            request=request,
            exception=e,
        )
        return JsonResponse({'error': 'Failed to fetch live system status data'}, status=502)