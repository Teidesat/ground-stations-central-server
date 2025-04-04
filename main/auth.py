from ninja.security import HttpBearer
from django.conf import settings

class SimpleTokenAuth(HttpBearer):
    def authenticate(self, request, token):
        if token == settings.API_TOKEN:
            return "ok" 
        return None
