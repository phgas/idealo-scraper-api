from django.http import JsonResponse
from .models import APIKey
import uuid

WHITELISTED_IPS = ['127.0.0.1']
SECRET_TOKEN = "YOUR_SECRET_TOKEN"


def validate_uuid_v4(value):
    try:
        parsed_uuid = uuid.UUID(value, version=4)
        return parsed_uuid.version == 4
    except ValueError:
        return False


def restrict_ip_address(view_func):
    def _wrapped_view_func(request, *args, **kwargs):
        if request.META['REMOTE_ADDR'] not in WHITELISTED_IPS:
            return JsonResponse({"detail": "Forbidden"}, status=403)
        return view_func(request, *args, **kwargs)
    return _wrapped_view_func


def require_api_key(view_func):
    def _wrapped_view_func(request, *args, **kwargs):
        api_key = request.headers.get('X-API-Key')
        if not api_key:
            return JsonResponse({"detail": "No API Key provided"}, status=401)
        elif validate_uuid_v4(api_key) == False or not APIKey.objects.filter(key=api_key, is_active=True).exists():
            return JsonResponse({"detail": "Invalid API Key"}, status=401)
        return view_func(request, *args, **kwargs)
    return _wrapped_view_func
