from utils.serializers import BaseSerializer

class SatelliteDataSerializer(BaseSerializer):
    def __init__(self, to_serialize, *, fields=[], request=None):
        super().__init__(to_serialize, fields=fields, request=request)

    def serialize_instance(self, instance) -> dict:
        return {
            'id': instance.pk,
            'category': instance.get_category_display(),
            'content': instance.content,
            'timestamp': instance.timestamp.isoformat(),
        }