import httpx
from celery import shared_task

@shared_task
def obtener_datos_buffer():
    API_URL = "http://127.0.0.1:8000/api"
    response = httpx.get(API_URL)
    return response.json()