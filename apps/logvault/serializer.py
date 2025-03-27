from utils.serializers import BaseSerializer

class LogSerializer(BaseSerializer):
    def __init__(self, to_serialize, *, fields=[], request=None):
        super().__init__(to_serialize, fields=fields, request=request)

    def serialize_instance(self, instance) -> dict:
        return {
            'id': instance.pk,
            'timestamp': instance.timestamp.isoformat(),
            'level': instance.level,
            'logger': instance.logger,
            'module': instance.module,
            'function': instance.function,
            'message': instance.message,
            'request_method': instance.request_method,
            'request_path': instance.request_path,
            'request_status_code': instance.request_status_code,
            'request_client_ip': instance.request_client_ip,
            'request_user': instance.request_user,
            'exception_type': instance.exception_type,
            'exception_message': instance.exception_message,
            'exception_stack_trace': instance.exception_stack_trace,
            'extra_data': instance.extra_data
        }