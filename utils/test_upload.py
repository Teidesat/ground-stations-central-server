import io
import json
import os
import random
from datetime import datetime

import requests
from PIL import Image

API_TOKEN = 'holis123'
NUM_IMAGENES = 0
NUM_DATOS_SATELLITE = 100
MEDIA_DIR = 'test-media-img'
CATEGORY_CHOICES = ['TEMP', 'POWR', 'HUMI', 'POSI', 'GENE']
BASE_URL = 'http://127.0.0.1:8000/api/'


def ensure_directory_exists(directory):
    """Crea un directorio si no existe."""
    os.makedirs(directory, exist_ok=True)


def save_binary_file(filepath, data):
    """Guarda datos binarios en un archivo."""
    with open(filepath, 'wb') as f:
        f.write(data)


def generate_images():
    """Genera imágenes de prueba y las guarda en el directorio MEDIA_DIR."""
    for i in range(NUM_IMAGENES):
        img = Image.new('RGB', (100, 100), color='red')
        img_bytes = io.BytesIO()
        img.save(img_bytes, format='PNG')
        save_binary_file(os.path.join(MEDIA_DIR, f'test_image_{i}.png'), img_bytes.getvalue())


def generate_binary_data():
    """Genera un archivo de datos binarios y lo guarda en MEDIA_DIR."""
    save_binary_file(os.path.join(MEDIA_DIR, 'test_data.bin'), os.urandom(1024))


def generate_satellite_data():
    """Genera archivos de datos satelitales simulados."""
    for i in range(NUM_DATOS_SATELLITE):
        data = {
            'category': random.choice(CATEGORY_CHOICES),
            'content': {'value': random.uniform(10, 100)},
            'timestamp': datetime.utcnow().isoformat() + 'Z',
        }
        binary_data = json.dumps(data).encode('utf-8')
        save_binary_file(os.path.join(MEDIA_DIR, f'satellite_data_{i}.bin'), binary_data)


def send_files():
    """Envía los archivos generados al servidor usando una solicitud POST."""
    headers = {'Authorization': f'Bearer {API_TOKEN}'}
    files = []

    for i in range(NUM_IMAGENES):
        filepath = os.path.join(MEDIA_DIR, f'test_image_{i}.png')
        files.append(('files', (f'test_image_{i}.png', open(filepath, 'rb'), 'image/png')))

    binary_file = os.path.join(MEDIA_DIR, 'test_data.bin')
    files.append(('files', ('test_data.bin', open(binary_file, 'rb'), 'application/octet-stream')))

    for i in range(NUM_DATOS_SATELLITE):
        filepath = os.path.join(MEDIA_DIR, f'satellite_data_{i}.bin')
        files.append(
            ('files', (f'satellite_data_{i}.bin', open(filepath, 'rb'), 'application/octet-stream'))
        )

    response = requests.post(BASE_URL, headers=headers, files=files)
    print(response.text)


if __name__ == '__main__':
    ensure_directory_exists(MEDIA_DIR)
    generate_images()
    generate_binary_data()
    generate_satellite_data()
    send_files()
