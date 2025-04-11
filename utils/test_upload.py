import json
import os
import random
from datetime import datetime, timedelta

import requests
from PIL import Image, ImageDraw

API_TOKEN = 'holis123'
NUM_IMAGENES = 10
NUM_DATOS_SATELLITE = 15
TEST_MEDIA_DIR = 'test-media-img'
MEDIA_DIR = './media'

CATEGORY_CHOICES = ['TEMP', 'POWR', 'HUMI', 'POSI', 'GENE']


def crear_directorio(directorio):
    """Crea un directorio si no existe."""
    if not os.path.exists(directorio):
        os.makedirs(directorio)


def limpiar_directorio(directorio):
    """Elimina todos los archivos en el directorio dado."""
    if os.path.exists(directorio):
        for archivo in os.listdir(directorio):
            ruta_archivo = os.path.join(directorio, archivo)
            if os.path.isfile(ruta_archivo):
                os.remove(ruta_archivo)


def generar_imagenes():
    """Genera imágenes aleatorias y las guarda en el directorio TEST_MEDIA_DIR."""
    crear_directorio(TEST_MEDIA_DIR)
    limpiar_directorio(TEST_MEDIA_DIR)

    for i in range(NUM_IMAGENES):
        width, height = 300, 300
        img = Image.new(
            'RGB',
            (width, height),
            color=(random.randint(0, 255), random.randint(0, 255), random.randint(0, 255)),
        )
        draw = ImageDraw.Draw(img)

        # Rellenar la imagen con puntos de color aleatorio
        for y in range(height):
            for x in range(width):
                r = (x + y) % 256
                g = (x * y) % 256
                b = (x - y) % 256
                draw.point((x, y), fill=(r, g, b))

        draw.text(
            (random.randint(10, 50), random.randint(10, 50)), f'Img {i}', fill=(255, 255, 255)
        )

        # Dibujar formas aleatorias
        for _ in range(random.randint(5, 15)):
            shape_type = random.choice(['circle', 'rectangle', 'line'])
            x1, y1 = random.randint(0, width), random.randint(0, height)
            x2, y2 = random.randint(0, width), random.randint(0, height)

            x1, x2 = min(x1, x2), max(x1, x2)
            y1, y2 = min(y1, y2), max(y1, y2)

            color = (random.randint(0, 255), random.randint(0, 255), random.randint(0, 255))
            if shape_type == 'circle':
                draw.ellipse([x1, y1, x2, y2], outline=color, width=2)
            elif shape_type == 'rectangle':
                draw.rectangle([x1, y1, x2, y2], outline=color, width=2)
            elif shape_type == 'line':
                draw.line([x1, y1, x2, y2], fill=color, width=2)

        # Guardar la imagen generada
        img_path = os.path.join(TEST_MEDIA_DIR, f'test_image_{i}.png')
        img.save(img_path, format='PNG')
        print(f'Imagen generada: {img_path}')


def generar_datos_binarios():
    """Genera un archivo binario con datos aleatorios solo si NUM_DATOS_SATELLITE es mayor que 0."""
    if NUM_DATOS_SATELLITE <= 0:
        print('No se generarán datos binarios porque NUM_DATOS_SATELLITE es 0 o menor.')
        return

    # Crear el archivo binario solo si es necesario
    binary_path = os.path.join(MEDIA_DIR, 'test_data.bin')
    with open(binary_path, 'wb') as f:
        f.write(os.urandom(1024))  # Escribe datos aleatorios de 1024 bytes
        print(f'Datos binarios generados: {binary_path}')


def generar_datos_satellite():
    """Genera archivos binarios con datos de satélite en formato JSON."""
    base_time = datetime.utcnow()
    for i in range(NUM_DATOS_SATELLITE):
        category = random.choice(CATEGORY_CHOICES)
        value_range = {
            'TEMP': (0, 50),
            'POWR': (0, 100),
            'HUMI': (0, 100),
            'POSI': (-180, 180),
            'GENE': (0, 1000),
        }

        value = round(random.uniform(*value_range[category]), 2)
        content = {'value': value}

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
        satellite_path = os.path.join(MEDIA_DIR, f'satellite_data_{i}.bin')
        with open(satellite_path, 'wb') as f:
            f.write(binary_data)
        print(f'Dato satelital generado: {satellite_path}')


def enviar_archivos():
    """Envía los archivos generados al servidor."""
    url = 'http://127.0.0.1:8000/api/'
    headers = {'Authorization': f'Bearer {API_TOKEN}'}

    files = []

    # Incluir imágenes
    for i in range(NUM_IMAGENES):
        img_path = os.path.join(TEST_MEDIA_DIR, f'test_image_{i}.png')
        if os.path.exists(img_path):
            files.append(
                (
                    'files',
                    (
                        f'test_image_{i}.png',
                        open(img_path, 'rb'),
                        'image/png',
                    ),
                )
            )

    # Incluir datos binarios si existen
    binary_path = os.path.join(MEDIA_DIR, 'test_data.bin')
    if os.path.exists(binary_path):
        files.append(
            (
                'files',
                (
                    'test_data.bin',
                    open(binary_path, 'rb'),
                    'application/octet-stream',
                ),
            )
        )

    # Incluir datos satelitales si existen
    for i in range(NUM_DATOS_SATELLITE):
        satellite_path = os.path.join(MEDIA_DIR, f'satellite_data_{i}.bin')
        if os.path.exists(satellite_path):
            files.append(
                (
                    'files',
                    (
                        f'satellite_data_{i}.bin',
                        open(satellite_path, 'rb'),
                        'application/octet-stream',
                    ),
                )
            )

    if not files:
        print('No hay archivos para enviar.')
        return

    # Enviar los archivos al servidor
    response = requests.post(url, headers=headers, files=files)
    print(response.text)


if __name__ == '__main__':
    crear_directorio(MEDIA_DIR)
    generar_imagenes()
    generar_datos_binarios()
    generar_datos_satellite()
    enviar_archivos()
