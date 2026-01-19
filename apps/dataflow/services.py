import httpx
from apps.core.models import GeneralData, SatelliteData, RadioStationData, OpticalStationData, FomalhautData
from django.utils import timezone

async def store_general_data(data: dict):
    data = GeneralData.objects.acreate(
        data_type=data.get('data_type'),
        data_source=data.get('data_source'),
        data_destination=data.get('data_destination'),
        content=data.get('content'),
        timestamp=timezone.now(),
        raw_data=data.get('raw_data')
    )
    return data

async def store_satellite_data(data: dict):
    data = SatelliteData.objects.acreate(
        data_type=data.get('data_type'),
        data_source=data.get('data_source'),
        data_destination=data.get('data_destination'),
        content=data.get('content'),
        timestamp=timezone.now(),
        raw_data=data.get('raw_data'),
        category=data.get('category')
    )
    return data

async def store_radio_station_data(data: dict):
    data = RadioStationData.objects.acreate(
        data_type=data.get('data_type'),
        data_source=data.get('data_source'),
        data_destination=data.get('data_destination'),
        content=data.get('content'),
        timestamp=timezone.now(),
        raw_data=data.get('raw_data'),
        category=data.get('category')
    )
    return data

async def store_optical_station_data(data: dict):
    data = OpticalStationData.objects.acreate(
        data_type=data.get('data_type'),
        data_source=data.get('data_source'),
        data_destination=data.get('data_destination'),
        content=data.get('content'),
        timestamp=timezone.now(),
        raw_data=data.get('raw_data'),
        category=data.get('category')
    )
    return data


async def store_fomalhaut_data(data: dict):
    data = FomalhautData.objects.acreate(
        data_type=data.get('data_type'),
        data_source=data.get('data_source'),
        data_destination=data.get('data_destination'),
        content=data.get('content'),
        timestamp=timezone.now(),
        raw_data=data.get('raw_data'),
        category=data.get('category')
    )
    return data

async def send_data(url: str, data: dict):
    async with httpx.AsyncClient() as client: # possible timeout addition
        response = await client.post(url, json=data)
        response.raise_for_status()
    return response.json()
    
        