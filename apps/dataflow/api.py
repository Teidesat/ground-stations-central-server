from ninja import Router, Query
from django.http import JsonResponse
# from asgiref.sync import sync_to_async
from typing import List
import httpx

from apps.core.models import GeneralData, SatelliteData, RadioStationData, OpticalStationData, FomalhautData
from .schemas import DataFilterSchema, LiveDataFilter
from .services import send_data, store_satellite_data, store_radio_station_data, store_optical_station_data, store_fomalhaut_data

from apps.logvault.services import create_log
from main.settings import RGS_URL, OGS_URL, FOMALHAUT_URL

router = Router()


# Ruta de datos para el satélite
# GET (Información en tiempo real)
@router.get('/satellite/live')
async def live_satellite_data(request, filters: LiveDataFilter = Query(...)):

    rgs_url = f"{RGS_URL}/satellite/live"

    try:
        async with httpx.AsyncClient() as client: # Possible addition of timeout
            response = await client.get(rgs_url, params=filters.dict())
            if response.status_code != 200:
                await create_log(
                    level= 'ERROR',
                    logger='ground-stations-central-server',
                    module='dataflow.api',
                    function='live_satellite_data',
                    message= f'ERROR al obtener datos en tiempo real del satélite: {response.status_code}',
                    request=request,
                )
                return JsonResponse({'error': 'Failed to fetch live data from satellite'}, status=502)
            data = response.json()
            try:
                await store_satellite_data(data)
            except Exception as e:
                await create_log(
                    level= 'ERROR',
                    logger='ground-stations-central-server',
                    module='dataflow.api',
                    function='live_satellite_data',
                    message= f'ERROR al almacenar dato del satélite: {e}',
                    request=request,
                    exception=e,
                )
                
            await create_log(
                level= 'INFO',
                logger='ground-stations-central-server',
                module='dataflow.api',
                function='live_satellite_data',
                message= f'Datos en tiempo real del satélite obtenidos correctamente.',
                request=request
            )

            return JsonResponse(data, status=200)
    except httpx.RequestError as e:
        await create_log(
            level= 'ERROR',
            logger='ground-stations-central-server',
            module='dataflow.api',
            function='live_satellite_data',
            message= f'ERROR en la solicitud de datos en tiempo real del satélite: {e}',
            request=request,
            exception=e,
        )
        return JsonResponse({'error': 'Failed to fetch live data from satellite'}, status=502)
        

# GET (Todos los datos BD)
@router.get('/satellite/data', response=List[DataFilterSchema])
async def all_satellite_data(request, filters: DataFilterSchema = Query(...)):
    qs = SatelliteData.objects.all()
    qs = filters.filter(qs)
    exists = await qs.aexists()
    
    if not exists:
        await create_log(
            level= 'WARNING',
            logger='ground-stations-central-server',
            module='dataflow.api',
            function='all_satellite_data',
            message= f'No hay datos disponibles que coincidan con los filtros proporcionados',
            request=request
        )
        return JsonResponse({'error': 'No data available'}, status=404)
    
    await create_log(
        level= 'INFO',
        logger='ground-stations-central-server',
        module='dataflow.api',
        function='all_satellite_data',
        message= f'Petición realizada',
        request=request
    )

    results = [item async for item in qs]

    return results

#POST (Envio comandos al satélite)
@router.post('/satellite/live')
async def send_satellite_data(request, data: LiveDataFilter):
    try:
        await create_log(
            level= 'INFO',
            logger='ground-stations-central-server',
            module='dataflow.api',
            function='send_satellite_data',
            message= f'Enviando comandos al satélite',
            request=request
        )

        response = await send_data(
            RGS_URL + '/satellite/live', 
            data.dict()
        )

        await create_log(
            level= 'INFO',
            logger='ground-stations-central-server',
            module='dataflow.api',
            function='send_satellite_data',
            message= f'Comandos enviados al satélite correctamente',
            request=request
        )
        return JsonResponse({
            'status': 'success',
            'message': response
        },  status=200)

    except httpx.RequestError as e:
        await create_log(
            level= 'ERROR',
            logger='ground-stations-central-server',
            module='dataflow.api',
            function='send_satellite_data',
            message= f'ERROR en la solicitud de envío de comandos al satélite: {e}',
            request=request,
            exception=e,
        )
        return JsonResponse({'error': 'Failed to send commands to satellite'}, status=502)


# Ruta de datos para la estación de radio
# GET (Solicitar información de la estación de radio)
@router.get('/radio-station/live')
async def live_radio_station_data(request, filters: LiveDataFilter = Query(...)):

    rgs_url = f"{RGS_URL}/radio-station/live"

    try:
        async with httpx.AsyncClient() as client: # Possible addition of timeout
            response = await client.get(rgs_url, params=filters.dict())
            if response.status_code != 200:
                await create_log(
                    level= 'ERROR',
                    logger='ground-stations-central-server',
                    module='dataflow.api',
                    function='live_radio_station_data',
                    message= f'ERROR al obtener datos en tiempo real de la estación de radio: {response.status_code}',
                    request=request,
                )
                return JsonResponse({'error': 'Failed to fetch live data from radio station'}, status=502)
            
            data = response.json()
            try:
                await store_radio_station_data(data)
            except Exception as e:
                await create_log(
                    level= 'ERROR',
                    logger='ground-stations-central-server',
                    module='dataflow.api',
                    function='live_radio_station_data',
                    message= f'ERROR al almacenar dato de la estación de radio: {e}',
                    request=request,
                    exception=e,
                )
            await create_log(
                level= 'INFO',
                logger='ground-stations-central-server',
                module='dataflow.api',
                function='live_radio_station_data',
                message= f'Datos en tiempo real de la estación de radio obtenidos correctamente',
                request=request
            )
            return JsonResponse(data, status=200)
    except httpx.RequestError as e:
        await create_log(
            level= 'ERROR',
            logger='ground-stations-central-server',
            module='dataflow.api',
            function='live_radio_station_data',
            message= f'ERROR en la solicitud de datos en tiempo real de la estación de radio: {e}',
            request=request,
            exception=e,
        )
        return JsonResponse({'error': 'Failed to fetch live data from radio station'}, status=502)

# GET (Todos los datos BD)
@router.get('/radio-station/data', response=List[DataFilterSchema])
async def all_radio_station_data(request, filters: DataFilterSchema = Query(...)):
    qs = RadioStationData.objects.all()
    qs = filters.filter(qs)
    exists = await qs.aexists()
    
    if not exists:
        await create_log(
            level= 'WARNING',
            logger='ground-stations-central-server',
            module='dataflow.api',
            function='all_radio_station_data',
            message= f'No hay datos disponibles que coincidan con los filtros proporcionados',
            request=request
        )
        return JsonResponse({'error': 'No data available'}, status=404)
    
    await create_log(
        level= 'INFO',
        logger='ground-stations-central-server',
        module='dataflow.api',
        function='all_radio_station_data',
        message= f'Petición realizada',
        request=request
    )

    results = [item async for item in qs]

    return results
    
# POST (Envio datos de la estación de radio)
@router.post('/radio-station/live')
async def send_radio_station_data(request, data: LiveDataFilter): 
    try:
        await create_log(
            level= 'INFO',
            logger='ground-stations-central-server',
            module='dataflow.api',
            function='send_radio_station_data',
            message= f'Enviando datos a la estación de radio',
            request=request
        )

        response = await send_data(
            RGS_URL + '/radio-station/live', 
            data.dict()
        )

        await create_log(
            level= 'INFO',
            logger='ground-stations-central-server',
            module='dataflow.api',
            function='send_radio_station_data',
            message= f'Datos enviados a la estación de radio correctamente',
            request=request
        )
        return JsonResponse({
            'status': 'success',
            'message': response
        },  status=200)
    
    except httpx.RequestError as e:
        await create_log(
            level= 'ERROR',
            logger='ground-stations-central-server',
            module='dataflow.api',
            function='send_radio_station_data',
            message= f'ERROR en la solicitud de envío de datos a la estación de radio: {e}',
            request=request,
            exception=e,
        )
        return JsonResponse({'error': 'Failed to send data to radio station'}, status=502)

# Ruta de datos para la estación óptica
# GET (Solicitar información de la estación óptica)
@router.get('/optical-station/live')
async def live_optical_station_data(request, filters: LiveDataFilter = Query(...)):
    ogs_url = f"{OGS_URL}/optical-station/live"

    try:
        async with httpx.AsyncClient() as client: # Possible addition of timeout
            response = await client.get(ogs_url, params=filters.dict())
            if response.status_code != 200:
                await create_log(
                    level= 'ERROR',
                    logger='ground-stations-central-server',
                    module='dataflow.api',
                    function='live_optical_station_data',
                    message= f'ERROR al obtener datos en tiempo real de la estación óptica: {response.status_code}',
                    request=request,
                )
                return JsonResponse({'error': 'Failed to fetch live data from optical station'}, status=502)
            data = response.json()
            try:
                await store_optical_station_data(data)
            except Exception as e:
                await create_log(
                    level= 'ERROR',
                    logger='ground-stations-central-server',
                    module='dataflow.api',
                    function='live_optical_station_data',
                    message= f'ERROR al almacenar dato de la estación óptica: {e}',
                    request=request,
                    exception=e,
                )
            await create_log(
                level= 'INFO',
                logger='ground-stations-central-server',
                module='dataflow.api',
                function='live_optical_station_data',
                message= f'Datos en tiempo real de la estación óptica obtenidos correctamente',
                request=request
            )
            return JsonResponse(data, status=200)
    except httpx.RequestError as e:
        await create_log(
            level= 'ERROR',
            logger='ground-stations-central-server',
            module='dataflow.api',
            function='live_optical_station_data',
            message= f'ERROR en la solicitud de datos en tiempo real de la estación óptica: {e}',
            request=request,
            exception=e,
        )
        return JsonResponse({'error': 'Failed to fetch live data from optical station'}, status=502)

# GET (Todos los datos BD)
@router.get('/optical-station/data', response=List[DataFilterSchema])
async def all_optical_station_data(request, filters: DataFilterSchema = Query(...)):
    qs = OpticalStationData.objects.all()
    qs = filters.filter(qs)
    exists = await qs.aexists()

    if not exists:
        await create_log(
            level= 'WARNING',
            logger='ground-stations-central-server',
            module='dataflow.api',
            function='all_optical_station_data',
            message= f'No hay datos disponibles que coincidan con los filtros proporcionados',
            request=request
        )
        return JsonResponse({'error': 'No data available'}, status=404)
    await create_log(
        level= 'INFO',
        logger='ground-stations-central-server',
        module='dataflow.api',
        function='all_optical_station_data',
        message= f'Petición realizada',
        request=request
    )
    results = [item async for item in qs]
    return results

# POST (Envio datos de la estación óptica)
@router.post('/optical-station/live')
async def send_optical_station_data(request, data: LiveDataFilter):
    try:
        await create_log(
            level= 'INFO',
            logger='ground-stations-central-server',
            module='dataflow.api',
            function='send_optical_station_data',
            message= f'Enviando datos a la estación óptica',
            request=request
        )

        response = await send_data(
            OGS_URL + '/optical-station/live', 
            data.dict()
        )

        await create_log(
            level= 'INFO',
            logger='ground-stations-central-server',
            module='dataflow.api',
            function='send_optical_station_data',
            message= f'Datos enviados a la estación óptica correctamente',
            request=request
        )
        return JsonResponse({
            'status': 'success',
            'message': response
        },  status=200)
    
    except httpx.RequestError as e:
        await create_log(
            level= 'ERROR',
            logger='ground-stations-central-server',
            module='dataflow.api',
            function='send_optical_station_data',
            message= f'ERROR en la solicitud de envío de datos a la estación óptica: {e}',
            request=request,
            exception=e,
        )
        return JsonResponse({'error': 'Failed to send data to optical station'}, status=502)
    
# Ruta de datos para Fomalhaut
# GET (Solicitar información de Fomalhaut)
@router.get('/fomalhaut/live')
async def live_fomalhaut_data(request, filters: LiveDataFilter = Query(...)):
    fom_url = f"{FOMALHAUT_URL}/fomalhaut/live"

    try:
        async with httpx.AsyncClient() as client: # Possible addition of timeout
            response = await client.get(fom_url, params=filters.dict())
            if response.status_code != 200:
                await create_log(
                    level= 'ERROR',
                    logger='ground-stations-central-server',
                    module='dataflow.api',
                    function='live_fomalhaut_data',
                    message= f'ERROR al obtener datos en tiempo real de Fomalhaut: {response.status_code}',
                    request=request,
                )
                return JsonResponse({'error': 'Failed to fetch live data from Fomalhaut'}, status=502)
            data = response.json()
            try:
                await store_fomalhaut_data(data)
            except Exception as e:
                await create_log(
                    level= 'ERROR',
                    logger='ground-stations-central-server',
                    module='dataflow.api',
                    function='live_fomalhaut_data',
                    message= f'ERROR al almacenar dato de Fomalhaut: {e}',
                    request=request,
                    exception=e,
                )
            await create_log(
                level= 'INFO',
                logger='ground-stations-central-server',
                module='dataflow.api',
                function='live_fomalhaut_data',
                message= f'Datos en tiempo real de Fomalhaut obtenidos correctamente',
                request=request
            )
            return JsonResponse(data, status=200)
    except httpx.RequestError as e:
        await create_log(
            level= 'ERROR',
            logger='ground-stations-central-server',
            module='dataflow.api',
            function='live_fomalhaut_data',
            message= f'ERROR en la solicitud de datos en tiempo real de Fomalhaut: {e}',
            request=request,
            exception=e,
        )
        return JsonResponse({'error': 'Failed to fetch live data from Fomalhaut'}, status=502)

# GET (Todos los datos BD)
@router.get('/fomalhaut/data', response=List[DataFilterSchema])
async def all_fomalhaut_data(request, filters: DataFilterSchema = Query(...)):
    qs = FomalhautData.objects.all()
    qs = filters.filter(qs)
    exists = await qs.aexists()

    if not exists:
        await create_log(
            level= 'WARNING',
            logger='ground-stations-central-server',
            module='dataflow.api',
            function='all_fomalhaut_data',
            message= f'No hay datos disponibles que coincidan con los filtros proporcionados',
            request=request
        )
        return JsonResponse({'error': 'No data available'}, status=404)
    await create_log(
        level= 'INFO',
        logger='ground-stations-central-server',
        module='dataflow.api',
        function='all_fomalhaut_data',
        message= f'Petición realizada',
        request=request
    )
    results = [item async for item in qs]
    return results
    
    
# POST (Envio datos de Fomalhaut)
@router.post('/fomalhaut/live')
async def send_fomalhaut_data(request, data: LiveDataFilter): #Implement schema
    try:
        await create_log(
            level= 'INFO',
            logger='ground-stations-central-server',
            module='dataflow.api',
            function='send_fomalhaut_data',
            message= f'Enviando datos a Fomalhaut',
            request=request
        )

        response = await send_data(
            FOMALHAUT_URL + '/fomalhaut/live', 
            data.dict()
        )

        await create_log(
            level= 'INFO',
            logger='ground-stations-central-server',
            module='dataflow.api',
            function='send_fomalhaut_data',
            message= f'Datos enviados a Fomalhaut correctamente',
            request=request
        )
        return JsonResponse({
            'status': 'success',
            'message': response
        },  status=200)
    
    except httpx.RequestError as e:
        await create_log(
            level= 'ERROR',
            logger='ground-stations-central-server',
            module='dataflow.api',
            function='send_fomalhaut_data',
            message= f'ERROR en la solicitud de envío de datos a Fomalhaut: {e}',
            request=request,
            exception=e,
        )
        return JsonResponse({'error': 'Failed to send data to Fomalhaut'}, status=502)