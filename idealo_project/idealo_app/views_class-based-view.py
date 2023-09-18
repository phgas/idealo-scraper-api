import json
import time
from .decorators import restrict_ip_address, require_api_key
from modules import idealo
from django.utils.decorators import method_decorator
from .models import APIKey
import logging
from rest_framework.views import APIView
from rest_framework.response import Response
from django.shortcuts import render
from django.views import View

logger = logging.getLogger(__name__)
SECRET_KEY = 'YOUR_SECRET_KEY'


class IdealoData(APIView):
    allowed_methods = ['GET', 'POST']
    def get(self, request, region):
        start_time = time.time()
        try:
            sample_data = {
                "limit": 10,
                "minPrice": 10,
                "maxPrice": 2000,
                "includeCategories": [
                    "3686"
                ],
                "sort": "RELEVANCE",
                "region": region
            }
            is_payload_valid, validation_msg, items = idealo.Scraper().fetch(**sample_data)
            if is_payload_valid and items:
                return Response({'success': is_payload_valid, 'processing_time_ms': round((time.time() - start_time) * 1000, 2), 'data': items}, status=200)
            else:
                return Response({'success': is_payload_valid, 'error': validation_msg}, status=500)
        except Exception as e:
            return Response({'success': False, 'error': f'Error executing the script: {str(e)}'}, status=500)

    @method_decorator(require_api_key)
    def post(self, request):
        start_time = time.time()
        try:
            data = json.loads(request.body.decode('utf-8'))
            is_payload_valid, validation_msg, items = idealo.Scraper().fetch(**data)
            if is_payload_valid and items:
                return Response({'success': is_payload_valid, 'processing_time_ms': round((time.time() - start_time) * 1000, 2), 'data': items}, status=200)
            else:
                return Response({'success': is_payload_valid, 'error': validation_msg}, status=400)
        except json.JSONDecodeError:
            return Response({'success': False, 'error': 'Request must be JSON'}, status=415)
        except Exception as e:
            logger.error(f'Error executing the script: {str(e)}')
            return Response({'success': False, 'error': 'Error retrieving data.'}, status=500)


class GenerateAPIKey(APIView):
    allowed_methods = ['POST']
    @method_decorator(restrict_ip_address)
    def post(self, request):
        start_time = time.time()
        if request.headers.get("Authorization") != SECRET_KEY:
            return Response({'success': False, 'error': 'Unauthorized'}, status=401)
        try:
            data = json.loads(request.body.decode('utf-8'))
            email = data.get('email')
            subscription_type = data.get('subscription_type')
            if not email:
                return Response({'success': False, 'error': 'Email is required!'}, status=400)
            elif not subscription_type:
                return Response({'success': False, 'error': 'Subscription type is required!'}, status=400)
            elif subscription_type not in ["free", "basic", "premium"]:
                return Response({'success': False, 'error': 'Subscription type is invalid!'}, status=400)
        except json.JSONDecodeError:
            return Response({'success': False, 'error': 'Request must be JSON'}, status=415)

        if APIKey.objects.filter(email=email).exists():
            return Response({'success': False, 'error': 'An API key for this email already exists!'}, status=400)

        api_key_instance = APIKey(
            email=email, subscription_type=subscription_type)
        api_key_instance.save()
        return Response({'success': True, 'processing_time_ms': round((time.time() - start_time) * 1000, 2), 'api_key': str(api_key_instance.key)}, status=200)


class LandingPage(View):
    def get(self, request, *args, **kwargs):
        context = {
            'message': "Hello from Django!"
        }
        return render(request, 'myself_page.html', context)
