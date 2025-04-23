import json
import os
import random
from contextlib import closing
from datetime import datetime, timedelta, timezone

import requests
from PIL import Image, ImageDraw

API_TOKEN = 'holis123'
NUM_IMAGENES = 60
NUM_DATOS_SATELLITE = 60
TEST_MEDIA_DIR = 'test-media-img'
MEDIA_DIR = './media'
EXAMPLES_DIR = 'examples'
IMAGE_EXTENSIONS = {'.png', '.jpg', '.jpeg', '.webp'}  # Modificado
CATEGORIAS = ['TEMP', 'POWR', 'HUMI', 'POSI']
URL_SERVIDOR = 'http://127.0.0.1:8000/api/'


def configurar_entorno():
    """Configura los directorios necesarios y limpia los existentes"""
    for directorio in [TEST_MEDIA_DIR, MEDIA_DIR, EXAMPLES_DIR]:
        try:
            os.makedirs(directorio, exist_ok=True)
            if directorio != EXAMPLES_DIR:
                for archivo in os.listdir(directorio):
                    ruta = os.path.join(directorio, archivo)
                    if os.path.isfile(ruta):
                        os.unlink(ruta)
        except OSError as error:
            print(f'Error configurando {directorio}: {error}')
            raise


def generar_textura_aleatoria(ancho: int, alto: int) -> list:
    """Genera una textura de píxeles optimizada"""
    return [
        ((x + y) % 256, (x * y) % 256, abs(x - y) % 256) for y in range(alto) for x in range(ancho)
    ]


def crear_imagen(numero: int, ancho=300, alto=300):
    """Crea una imagen con validación de coordenadas"""
    try:
        img = Image.new('RGB', (ancho, alto))
        img.putdata(generar_textura_aleatoria(ancho, alto))

        dibujo = ImageDraw.Draw(img)
        dibujo.text((10, 10), f'Img {numero}', fill=(255, 255, 255))

        for _ in range(random.randint(5, 15)):
            x1, x2 = sorted([random.randint(0, ancho), random.randint(0, ancho)])
            y1, y2 = sorted([random.randint(0, alto), random.randint(0, alto)])
            color = tuple(random.randint(0, 255) for _ in range(3))

            forma = random.choice(['ellipse', 'rectangulo', 'linea'])
            if forma == 'ellipse':
                dibujo.ellipse([x1, y1, x2, y2], outline=color, width=2)
            elif forma == 'rectangulo':
                dibujo.rectangle([x1, y1, x2, y2], outline=color, width=2)
            else:
                dibujo.line([x1, y1, x2, y2], fill=color, width=2)

        img.save(os.path.join(TEST_MEDIA_DIR, f'test_image_{numero}.png'), optimize=True)
        print(f'Imagen {numero + 1} generada')
    except Exception as error:
        print(f'Error generando imagen: {error}')


def generar_archivo_binario():
    """Genera archivo binario principal"""
    try:
        ruta = os.path.join(MEDIA_DIR, 'test_data.bin')
        with open(ruta, 'wb') as archivo:
            archivo.write(os.urandom(1024))
        print(f'Binario generado: {ruta}')
    except IOError as error:
        print(f'Error generando binario: {error}')


def generar_dato_satelital(id_dato: int, timestamp_base: datetime):
    """Genera datos de telemetría simulados con unidades específicas"""
    try:
        categoria = random.choice(CATEGORIAS)
        contenido = {}

        match categoria:
            case 'TEMP':
                contenido = {'value': round(random.uniform(0, 50), 2), 'unit': '°C'}

            case 'HUMI' | 'POWR':  # Mismo manejo para ambas categorías
                contenido = {
                    'value': round(random.uniform(0, 100)),
                    'unit': '%',
                }

            case 'POSI':
                contenido = {
                    'latitude': round(random.uniform(-90, 90), 6),
                    'longitude': round(random.uniform(-180, 180), 6),
                }

        dato = {
            'category': categoria,
            'content': contenido,
            'timestamp': (timestamp_base - timedelta(seconds=random.randint(0, 3600)))
            .isoformat()
            .replace('+00:00', 'Z'),
        }

        ruta = os.path.join(MEDIA_DIR, f'satellite_data_{id_dato}.bin')
        with open(ruta, 'wb') as archivo:
            archivo.write(json.dumps(dato).encode('utf-8'))
        print(f'Dato satelital {id_dato + 1} generado')
    except Exception as error:
        print(f'Error generando dato satelital: {error}')


def agregar_imagenes_examples(archivos, handles):
    """Agrega imágenes desde el directorio examples a la lista de archivos"""
    if not os.path.isdir(EXAMPLES_DIR):
        print(f'Directorio {EXAMPLES_DIR} no encontrado, omitiendo imágenes de ejemplo')
        return

    print('\nAgregando imágenes desde examples:')
    for filename in os.listdir(EXAMPLES_DIR):
        file_ext = os.path.splitext(filename)[1].lower()
        if file_ext in IMAGE_EXTENSIONS:
            ruta = os.path.join(EXAMPLES_DIR, filename)
            try:
                handle = open(ruta, 'rb')
                handles.append(handle)

                # Determinar MIME type
                if file_ext == '.webp':
                    mime_type = 'image/webp'
                elif file_ext in ('.jpg', '.jpeg'):
                    mime_type = 'image/jpeg'
                else:
                    mime_type = 'image/png'

                archivos.append(('files', (filename, handle, mime_type)))
                print(f'✅ {filename} (tipo: {mime_type})')
            except Exception as e:
                print(f'❌ Error cargando {filename}: {str(e)}')


def subir_archivos():
    """Envía archivos al servidor incluyendo imágenes de examples"""
    archivos = []
    handles = []

    try:
        # Imágenes generadas en TEST_MEDIA_DIR
        for i in range(NUM_IMAGENES):
            ruta = os.path.join(TEST_MEDIA_DIR, f'test_image_{i}.png')
            if os.path.exists(ruta):
                handle = open(ruta, 'rb')
                handles.append(handle)
                archivos.append(('files', (f'imagen_{i}.png', handle, 'image/png')))

        # Agregar imágenes de examples
        agregar_imagenes_examples(archivos, handles)

        # Archivo binario principal
        ruta_binario = os.path.join(MEDIA_DIR, 'test_data.bin')
        if os.path.exists(ruta_binario):
            handle = open(ruta_binario, 'rb')
            handles.append(handle)
            archivos.append(('files', ('datos.bin', handle, 'application/octet-stream')))

        # Datos satelitales
        for i in range(NUM_DATOS_SATELLITE):
            ruta = os.path.join(MEDIA_DIR, f'satellite_data_{i}.bin')
            if os.path.exists(ruta):
                handle = open(ruta, 'rb')
                handles.append(handle)
                archivos.append(
                    ('files', (f'satellite_{i}.bin', handle, 'application/octet-stream'))
                )

        if not archivos:
            print('No hay archivos para enviar')
            return

        with closing(
            requests.post(
                URL_SERVIDOR,
                headers={'Authorization': f'Bearer {API_TOKEN}'},
                files=archivos,
                timeout=30,
            )
        ) as respuesta:
            respuesta.raise_for_status()
            print(f'Respuesta del servidor: {respuesta.text}')

    except requests.RequestException as error:
        print(f'Error de conexión: {error}')
    finally:
        for handle in handles:
            try:
                handle.close()
            except Exception as error:
                print(f'Error cerrando archivo: {error}')


if __name__ == '__main__':
    try:
        configurar_entorno()

        for i in range(NUM_IMAGENES):
            crear_imagen(i)

        generar_archivo_binario()

        timestamp_base = datetime.now(timezone.utc)
        for i in range(NUM_DATOS_SATELLITE):
            generar_dato_satelital(i, timestamp_base)

        subir_archivos()

    except KeyboardInterrupt:
        print('\nEjecución cancelada por el usuario')
    except Exception as error:
        print(f'Error crítico: {error}')
