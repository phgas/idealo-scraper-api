from django.urls import path
from .views import idealo_data_get, idealo_data_post, generate_key, LandingPage

urlpatterns = [
    path('data/idealo/<str:region>', idealo_data_get, name='idealo_data'),
    path('data/idealo', idealo_data_post, name='idealo_data'),
    path('generate_key', generate_key, name='generate_key'),
    path('', LandingPage.as_view(), name='Landing Page'),
]
