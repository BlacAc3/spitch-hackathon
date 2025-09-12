from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse, JsonResponse
from django.views.decorators.cache import cache_page
from django.conf import settings
from spitch import Spitch
from .models import Proverb  # Import the Proverb model
from django.core.files.base import ContentFile
import io

# Create your views here.


def home(request):
    return render(request, 'proverbs/home.html')



@cache_page(60 * 60 * 24)  # Cache for 24 hours
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
    generate_tts(proverb)  # Generate TTS and get URL
    context = {'proverb': proverb}
    print(proverb.audio.url)
    return render(request, 'proverbs/tts_proverb.html', context)


# Placeholder for the new /api/generate-tts/ endpoint
# You will need to implement the actual TTS generation logic here

def generate_tts(proverb):
    client = Spitch(api_key=settings.SPITCH_API_KEY)

    response = client.speech.generate(
        text=proverb.text,
        language="yo",
        voice="sade"
    )

    audio_content = response.read()

    # Create an in-memory file-like object
    audio_file = ContentFile(audio_content, name=f"{proverb.text[:20]}.mp3")

    # Save the audio file to the proverb object
    proverb.audio.save(f"{proverb.text[:20]}.mp3", audio_file, save=False)
    proverb.save()

    return
