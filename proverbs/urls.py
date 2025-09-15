from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('proverbs/', views.proverb_list, name='proverb_list'),
    path('proverb/add/', views.input_proverb, name='input_proverb'),
    path('proverbs/<int:proverb_id>/', views.tts_proverb, name='tts_proverb'),
    path('rate/', views.rate_proverb, name='rate_general'),
    path('proverbs/<int:proverb_id>/rate/', views.rate_proverb, name='rate_proverb'),
    path('results/', views.rating_results, name='rating_results_general'),
    path('proverbs/<int:proverb_id>/results/', views.rating_results, name='rating_results_proverb'),
    path('api/generate-tts/', views.generate_tts_api, name='generate_tts_api'),
]
