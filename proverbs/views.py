from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse, JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json
from django.conf import settings
from spitch import Spitch
from .models import Proverb  # Import the Proverb model

# Create your views here.


def home(request):
    return render(request, 'proverbs/home.html')


def proverb_list(request):
    proverbs = Proverb.objects.all().order_by('text')  # Fetch all proverbs from the database
    context = {'proverbs': proverbs}
    return render(request, 'proverbs/proverb_list.html', context)


def input_proverb(request):
    if request.method == 'POST':
        proverb_text = request.POST.get('proverb_text')
        translation_text = request.POST.get('translation_text')  # Get translation text

        if proverb_text:  # Ensure there's text to save
            Proverb.objects.create(text=proverb_text, translation=translation_text)
            return redirect('proverb_list')  # Redirect to proverb list after successful submission
    return render(request, 'proverbs/input_proverb.html')


def tts_proverb(request, proverb_id):
    proverb = get_object_or_404(Proverb, pk=proverb_id)  # Fetch proverb by ID
    audio_url = generate_tts(proverb.text)  # Generate TTS and get URL
    context = {'proverb': proverb, 'audio_url': audio_url}
    return render(request, 'proverbs/tts_proverb.html', context)


# Placeholder for the new /api/generate-tts/ endpoint
# You will need to implement the actual TTS generation logic here

def generate_tts(text):
    import os
    client = Spitch(api_key=settings.SPITCH_API_KEY)
    hashed_text = hash(text)
    filename = f"generated_tts_{hashed_text}.mp3"
    filepath = f"static/audio/{filename}"
    os.makedirs(os.path.dirname(filepath), exist_ok=True)
    with open(filepath, "wb") as f:
        response = client.speech.generate(
            text=text,
            language="yo",
            voice="sade"
        )
        f.write(response.read())

    # For now, just a mock response
    mock_audio_url = f"/{filepath}"  # Mock URL
    return mock_audio_url
