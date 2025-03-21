from apps.analyze_image.models import Imagen
from ninja import File, UploadedFile
from datetime import datetime
from io import BytesIO
from PIL import ExifTags, Image


def subir_imagen(imagen:UploadedFile = File(...)):
    try:
        img = Image.open(imagen.file)
    except:
        return {'error': 'Archivo no es una imagen válida'}

    metadata = {
        'formato': img.format,
        'modo': img.mode,
        'tamaño': img.size,
    }

    output = BytesIO()
    img.convert('RGB').save(output, format='JPEG')

    exif_data = img.getexif()

    exif_dict = {}
    for tag_id, valor in exif_data.items():
        tag_nombre = ExifTags.TAGS.get(tag_id, tag_id)
        exif_dict[tag_nombre] = valor

    print(exif_dict)

    if 'DateTime' in exif_dict:
        date = datetime.strptime(exif_dict['DateTime'], '%Y:%m:%d %H:%M:%S')

        img = Imagen.objects.create(content=imagen, header=metadata, exif=exif_dict, fecha=date)

    # img = Imagen.objects.create(content=imagen, header=metadata, exif=exif_dict)

    return 'Ok'