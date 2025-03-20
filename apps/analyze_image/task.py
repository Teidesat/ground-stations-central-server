import httpx
import asyncio

async def obtener_datos_buffer():
    API_URL = "http://127.0.0.1:8000/api/buffer/get"  
    response =  httpx.get(API_URL)
    return response.json()