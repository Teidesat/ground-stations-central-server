import ast
import asyncio
from datetime import datetime
from io import BytesIO

import httpx
from django.http import HttpRequest
from ninja import File, Router, UploadedFile
from PIL import ExifTags, Image

from .models import Imagen
from .schemas import ImageSchema
from .task import obtener_datos_buffer
router = Router()


