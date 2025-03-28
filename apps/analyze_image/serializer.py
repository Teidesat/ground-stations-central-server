from utils.serializers import BaseSerializer

class ImageSerializer(BaseSerializer):
    def __init__(self, to_serialize, *, fields=[], request=None):
        super().__init__(to_serialize, fields=fields, request=request)

    def serialize_instance(self, instance) -> dict:
        return {
            'id': instance.pk,
            'format': instance.format,
            'header': instance.header,
            'exif': instance.exif,
            'created_at': instance.created_at,
            'content': self.build_url(instance.content.url),
        }