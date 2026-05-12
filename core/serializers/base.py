"""
Base serializer for consistent JSON responses across the application.
"""

from django.urls import reverse
from typing import Any, List, Optional, Union
from django.db.models import QuerySet
from django.http import HttpRequest
import json


class BaseSerializer:
    """
    Base serializer class that all app serializers should inherit from.
    Provides common functionality like URL building and JSON responses.
    """
    
    def __init__(self, to_serialize: Union[Any, QuerySet, List[Any]], *, fields: List[str] = [], request: Optional[HttpRequest] = None):
        """
        Initialize the serializer.
        
        Args:
            to_serialize: Single instance, queryset, or list of instances
            fields: Specific fields to serialize (empty = all fields)
            request: HTTP request object for building absolute URLs
        """
        self.to_serialize = to_serialize
        self.fields = fields
        self.request = request
        self._is_list = isinstance(to_serialize, (QuerySet, list)) and not isinstance(to_serialize, dict)
    
    def build_url(self, path: str) -> Optional[str]:
        """
        Build absolute URL from relative path.
        
        Args:
            path: Relative path (e.g., '/media/image.jpg')
            
        Returns:
            Absolute URL or None if path is empty or no request
        """
        if not path or not self.request:
            return path
        
        return self.request.build_absolute_uri(path)
    
    def serialize_instance(self, instance) -> dict:
        """
        Override this method in child classes.
        
        Args:
            instance: Model instance to serialize
            
        Returns:
            Dictionary representation of the instance
        """
        raise NotImplementedError("Subclasses must implement serialize_instance")
    
    def serialize(self) -> Union[dict, list]:
        """
        Serialize the data to a dictionary or list.
        
        Returns:
            Serialized data as dict (single) or list (multiple)
        """
        if self._is_list:
            return [self.serialize_instance(item) for item in self.to_serialize]
        else:
            return self.serialize_instance(self.to_serialize)
    
    def json_response(self) -> str:
        """
        Return JSON string representation.
        
        Returns:
            JSON string
        """
        return json.dumps(self.serialize())
    
    def dict_response(self) -> Union[dict, list]:
        """
        Return dictionary/list representation.
        
        Returns:
            Dictionary or list ready for JSON response
        """
        return self.serialize()