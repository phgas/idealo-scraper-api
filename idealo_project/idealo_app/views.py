import json
import time
import os
from .decorators import restrict_ip_address, require_api_key
from modules import idealo
from .models import APIKey
from django.db.models import F
import logging
from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.shortcuts import render
from django.views import View
from datetime import datetime, timedelta


logger = logging.getLogger(__name__)

SECRET_KEY = os.environ.get('SECRET_KEY')

REQUESTS_AMOUNT = {
    'free': '1000',
    'basic': '5000',
    'premium': '10000'
}


@api_view(['GET'])
def idealo_data_get(request, region):
    start_time = time.time()
    try:
        sample_data = {
            "limit": 10,
            "minPrice": 10,
            "maxPrice": 2000,
            "includeCategories": ["3686"],
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


@api_view(['POST'])
@require_api_key
def idealo_data_post(request):
    start_time = time.time()
    api_key_value = request.headers.get('X-API-Key')
    try:
        api_key_instance = APIKey.objects.get(key=api_key_value)
    except APIKey.DoesNotExist:
        return Response({'success': False, 'error': 'Invalid API Key'}, status=401)
    if api_key_instance.requests_left <= 0:
        if round(datetime.now().timestamp()) < api_key_instance.expiry:
            return Response({'success': False, 'error': f'Rate limited: Try again after {datetime.fromtimestamp(api_key_instance.expiry).strftime("%Y-%m-%d %H:%M:%S")}'}, status=429)
        else:
            api_key_instance.requests_left = REQUESTS_AMOUNT[api_key_instance.subscription_type]
            api_key_instance.save()
            pass
    try:
        data = json.loads(request.body.decode('utf-8'))
        is_payload_valid, validation_msg, items = idealo.Scraper().fetch(**data)
        if is_payload_valid and items:
            APIKey.objects.filter(key=api_key_value).update(
                requests_left=F('requests_left') - 1)
            return Response({'success': is_payload_valid, 'processing_time_ms': round((time.time() - start_time) * 1000, 2), 'data': items}, status=200)
        else:
            return Response({'success': is_payload_valid, 'error': validation_msg}, status=400)
    except json.JSONDecodeError:
        return Response({'success': False, 'error': 'Request must be JSON'}, status=415)
    except Exception as e:
        logger.error(f'Error executing the script: {str(e)}')
        return Response({'success': False, 'error': 'Error retrieving data.'}, status=500)


@api_view(['POST'])
@restrict_ip_address
def generate_key(request):
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
        elif subscription_type not in REQUESTS_AMOUNT:
            return Response({'success': False, 'error': 'Subscription type is invalid!'}, status=400)
    except json.JSONDecodeError:
        return Response({'success': False, 'error': 'Request must be JSON'}, status=415)

    if APIKey.objects.filter(email=email).exists():
        return Response({'success': False, 'error': 'An API key for this email already exists!'}, status=400)

    api_key_instance = APIKey(
        email=email, is_active=True, subscription_type=subscription_type, requests_left=REQUESTS_AMOUNT[subscription_type], expiry=round((datetime.now()+timedelta(days=30)).timestamp()))
    api_key_instance.save()
    return Response({'success': True, 'processing_time_ms': round((time.time() - start_time) * 1000, 2), 'api_key': str(api_key_instance.key)}, status=200)


class LandingPage(View):
    def get(self, request, *args, **kwargs):
        context = {
            'message': "Hello from Django!"
        }
        return render(request, 'myself_page.html', context)
