import json
from abc import ABC
from typing import Iterable

from django.http import HttpRequest, JsonResponse


class BaseSerializer(ABC):
    def __init__(
        self,
        to_serialize: object | Iterable[object],
        *,
        fields: Iterable[str] = [],
        request: HttpRequest = None,
    ):
        self.to_serialize = to_serialize
        self.fields = fields
        self.request = request

    def build_url(self, path: str) -> str:
        return self.request.build_absolute_uri(path) if self.request else path

    # To be implemented by subclasses
    def serialize_instance(self, instance: object) -> dict:
        raise NotImplementedError

    def __serialize_instance(self, instance: object) -> dict:
        serialized = self.serialize_instance(instance)
        return {f: v for f, v in serialized.items() if not self.fields or f in self.fields}

    def serialize(self) -> dict | list[dict]:
        if not isinstance(self.to_serialize, Iterable):
            return self.__serialize_instance(self.to_serialize)
        return [self.__serialize_instance(instance) for instance in self.to_serialize]

    def to_json(self) -> str:
        return json.dumps(self.serialize())

    def json_response(self) -> str:
        return JsonResponse(self.serialize(), safe=False)
