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


def rate_proverb(request, proverb_id):
    proverb = get_object_or_404(Proverb, pk=proverb_id)

    if request.method == 'POST':
        # Process the form data
        q1 = request.POST.get('q1')
        q2 = request.POST.get('q2')
        q3 = request.POST.get('q3')
        q4 = request.POST.get('q4')
        q5 = request.POST.get('q5')
        q6 = request.POST.get('q6')
        q7 = request.POST.get('q7')
        q8 = request.POST.get('q8')
        q9 = request.POST.get('q9')
        q10 = request.POST.get('q10')

        # Competence Check
        competence_score = 0
        if q1 == 'B':
            competence_score += 1
        if q2 == 'B':
            competence_score += 1
        if q3 == 'D':
            competence_score += 1

        # Proverb Evaluation Scores
        intelligibility_clarity = int(q4) if q4 else 0
        segmentation = 1 if q5 == 'B' else 0  # 1 if natural, 0 if unnatural
        tone_accuracy = int(q6) if q6 else 0
        naturalness_fluency = 0
        if q7 == 'D':
            naturalness_fluency = 5
        elif q7 == 'C':
            naturalness_fluency = 4
        elif q7 == 'B':
            naturalness_fluency = 2
        else:
            naturalness_fluency = 1

        accent_authenticity = 0
        if q8 == 'C':
            accent_authenticity = 5
        elif q8 == 'B':
            accent_authenticity = 3
        else:
            accent_authenticity = 1

        semantic_correctness = 0
        if q9 == 'C':
            semantic_correctness = 5
        elif q9 == 'B':
            semantic_correctness = 3
        else:
            semantic_correctness = 1

        overall_rating = int(q10) if q10 else 0

        # Calculate Average Proverb Evaluation Score
        proverb_evaluation_score = (intelligibility_clarity + segmentation * 5 + tone_accuracy + naturalness_fluency + accent_authenticity + semantic_correctness) / 6

        # Final Rating Logic - Adjust weights as needed
        final_rating = (0.3 * competence_score + 0.7 * proverb_evaluation_score)

        # Print the results (for debugging)
        print(f"Competence Score: {competence_score}")
        print(f"Proverb Evaluation Score: {proverb_evaluation_score}")
        print(f"Final Rating: {final_rating}")
        print(f"Rating for proverb {proverb_id}:")
        print(f"Q1: {q1}, Q2: {q2}, Q3: {q3}, Q4: {q4}, Q5: {q5}, Q6: {q6}, Q7: {q7}, Q8: {q8}, Q9: {q9}, Q10: {q10}")


        # Redirect back to the proverb list after submission
        return redirect('proverb_list')
    else:
        # Render the rating form
        context = {'proverb': proverb}
        return render(request, 'proverbs/tts_rating.html', context)

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
