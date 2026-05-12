# config/helper.py
"""Helper utilities for image processing (legacy module)."""

from datetime import datetime
from io import BytesIO

from ninja import File, UploadedFile
from PIL import ExifTags, Image

from apps.imaging.models import Imagen


def subir_imagen(imagen: UploadedFile = File(...)):
    """Upload and process an image file, extracting metadata and EXIF data.

    Args:
        imagen: The uploaded image file.

    Returns:
        String "Ok" on success, or error dict on failure.
    """
    try:
        img = Image.open(imagen.file)
    except Exception:
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
        Imagen.objects.create(content=imagen, header=metadata, exif=exif_dict, fecha=date)

    return 'Ok'