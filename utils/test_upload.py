import os
import io
import requests
from PIL import Image

NUM_IMAGENES = 30  
MEDIA_DIR = "test-media-img" 

def crear_directorio():
    if not os.path.exists(MEDIA_DIR):
        os.makedirs(MEDIA_DIR)

def generar_imagenes():
    
    for i in range(NUM_IMAGENES):
        img = Image.new('RGB', (100, 100), color='red')
        img_bytes = io.BytesIO()
        img.save(img_bytes, format='PNG')
        
        
        with open(os.path.join(MEDIA_DIR, f"test_image_{i}.png"), "wb") as f:
            f.write(img_bytes.getvalue())

def generar_datos_binarios():
    with open(os.path.join(MEDIA_DIR, "test_data.bin"), "wb") as f:
        f.write(os.urandom(1024))  

def enviar_archivos():
    url = "http://127.0.0.1:8000/api/"
    
    files = [
        ('files', (f'test_image_{i}.png', open(os.path.join(MEDIA_DIR, f'test_image_{i}.png'), 'rb'), 'image/png')) 
        for i in range(NUM_IMAGENES)
    ]


    files.append(('files', ('test_data.bin', open(os.path.join(MEDIA_DIR, 'test_data.bin'), 'rb'), 'application/octet-stream')))

    response = requests.post(url, files=files)
    print(response.text)

if __name__ == "__main__":
    crear_directorio()  
    generar_imagenes()  
    generar_datos_binarios()  
    enviar_archivos()  
