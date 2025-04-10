import json
import os
import random
from datetime import datetime, timedelta

import requests
from PIL import Image, ImageDraw

API_TOKEN = 'holis123'
NUM_IMAGENES = 0
NUM_DATOS_SATELLITE = 50
MEDIA_DIR = 'test-media-img'

CATEGORY_CHOICES = ['TEMP', 'POWR', 'HUMI', 'POSI', 'GENE']


def crear_directorio():
    if not os.path.exists(MEDIA_DIR):
        os.makedirs(MEDIA_DIR)


def generar_imagenes():
    for i in range(NUM_IMAGENES):
        img = Image.new(
            'RGB',
            (100, 100),
            color=(random.randint(0, 255), random.randint(0, 255), random.randint(0, 255)),
        )
        draw = ImageDraw.Draw(img)
        draw.text((10, 10), f'Img {i}', fill=(255, 255, 255))

        with open(os.path.join(MEDIA_DIR, f'test_image_{i}.png'), 'wb') as f:
            img.save(f, format='PNG')


def generar_datos_binarios():
    with open(os.path.join(MEDIA_DIR, 'test_data.bin'), 'wb') as f:
        f.write(os.urandom(1024))


def generar_datos_satellite():
    base_time = datetime.utcnow()
    for i in range(NUM_DATOS_SATELLITE):
        category = random.choice(CATEGORY_CHOICES)
        value_range = {
            'TEMP': (0, 50),  # Temperatura en °C
            'POWR': (0, 100),  # Potencia en %
            'HUMI': (0, 100),  # Humedad en %
            'POSI': (-180, 180),  # Coordenadas
            'GENE': (0, 1000),  # Datos generales
        }

        value = round(random.uniform(*value_range[category]), 2)
        content = {'value': value}

        # Agregar detalles específicos por categoría
        if category == 'TEMP':
            content['unit'] = '°C'
        elif category == 'POSI':
            content.update(
                {
                    'latitude': round(random.uniform(-90, 90), 6),
                    'longitude': round(random.uniform(-180, 180), 6),
                }
            )

        timestamp = (base_time - timedelta(seconds=random.randint(0, 3600))).isoformat() + 'Z'

        data = {
            'category': category,
            'content': content,
            'timestamp': timestamp,
        }

        binary_data = json.dumps(data).encode('utf-8')
        with open(os.path.join(MEDIA_DIR, f'satellite_data_{i}.bin'), 'wb') as f:
            f.write(binary_data)


def enviar_archivos():
    url = 'http://127.0.0.1:8000/api/'
    headers = {'Authorization': f'Bearer {API_TOKEN}'}

    files = [
        (
            'files',
            (
                f'test_image_{i}.png',
                open(os.path.join(MEDIA_DIR, f'test_image_{i}.png'), 'rb'),
                'image/png',
            ),
        )
        for i in range(NUM_IMAGENES)
    ]

    files.append(
        (
            'files',
            (
                'test_data.bin',
                open(os.path.join(MEDIA_DIR, 'test_data.bin'), 'rb'),
                'application/octet-stream',
            ),
        )
    )

    for i in range(NUM_DATOS_SATELLITE):
        files.append(
            (
                'files',
                (
                    f'satellite_data_{i}.bin',
                    open(os.path.join(MEDIA_DIR, f'satellite_data_{i}.bin'), 'rb'),
                    'application/octet-stream',
                ),
            )
        )

    response = requests.post(url, headers=headers, files=files)
    print(response.text)


if __name__ == '__main__':
    crear_directorio()
    generar_imagenes()
    generar_datos_binarios()
    generar_datos_satellite()
    enviar_archivos()
