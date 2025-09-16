import base64
import json
from django.http import JsonResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.views.decorators.cache import cache_page
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings
from spitch import Spitch
from . import models # Import models module directly
from django.core.files.base import ContentFile

# Create your views here.


@cache_page(60 * 60 * 24)  # Cache for 24 hours
def home(request):
    return render(request, 'proverbs/home.html')


@cache_page(60 * 60 * 24)  # Cache for 24 hours
def proverb_list(request):
    all_proverbs = models.Proverb.objects.all().order_by('text')

    system_proverbs = []
    user_proverbs = []

    for proverb in all_proverbs:
        if proverb.tag == 'system':
            system_proverbs.append(proverb)
        elif proverb.tag == 'user':  # Explicitly check for 'user' tag
            user_proverbs.append(proverb)

    context = {
        'system_proverbs': system_proverbs,
        'user_proverbs': user_proverbs,
    }
    return render(request, 'proverbs/proverb_list.html', context)

def input_proverb(request):
    if request.method == 'POST':
        proverb_text = request.POST.get('proverb_text')
        translation_text = request.POST.get('translation_text')  # Get translation text

        if proverb_text:  # Ensure there\'s text to save
            models.Proverb.objects.create(text=proverb_text, translation=translation_text, tag="user")
            return redirect('proverb_list')  # Redirect to proverb list after successful submission
    return render(request, 'proverbs/input_proverb.html')


def _calculate_competence_and_final_rating(q1, q2, q3, q4, q6, q10, proverb_rating):
    # --- Competence Score Calculation ---
    competence_score = 0
    if q1 == 'B':
        competence_score += 1
    if q2 == 'B':
        competence_score += 1
    if q3 == 'D':
        competence_score += 1

    # --- Competence Multiplier ---\
    competence_multiplier = 0.5 # Novice
    if competence_score == 2:
        competence_multiplier = 1.0 # Knowledgeable
    elif competence_score == 3:
        competence_multiplier = 1.5 # Expert

    # --- Final Rating Calculation based on rating_system.md ---\
    # Convert to int, default to 0 if not present (should be handled by form validation in production)\
    q4_int = int(q4) if q4 else 0
    q6_int = int(q6) if q6 else 0
    q10_int = int(q10) if q10 else 0

    final_rating_value = 0.0

    if proverb_rating:
        # For proverb-specific ratings, use Q4, Q6, Q10 as primary inputs
        if q4 and q6 and q10: # Ensure all required fields for formula are present
            raw_rating_sum = q4_int + q6_int + q10_int
            final_rating_value = (raw_rating_sum / 3) * competence_multiplier
        # If not all are present, final_rating_value remains 0.0 or handle error
    else:
        # For general rating, use available score questions (Q4, Q6, Q10) if submitted, else just Q10.
        submitted_scores_for_general = []
        if q4: submitted_scores_for_general.append(q4_int)
        if q6: submitted_scores_for_general.append(q6_int)
        if q10: submitted_scores_for_general.append(q10_int)

        if submitted_scores_for_general:
            avg_score = sum(submitted_scores_for_general) / len(submitted_scores_for_general)
            final_rating_value = avg_score * competence_multiplier
        # If no scores are submitted (shouldn\'t happen for q10, which is required), final_rating_value remains 0.0

    return competence_score, final_rating_value


def rate_proverb(request, proverb_id=None):
    proverb = None
    proverb_rating = False
    if proverb_id:
        proverb = get_object_or_404(models.Proverb, pk=proverb_id)
        proverb_rating = True

    if request.method == 'POST':
        # Retrieve all form data
        q1 = request.POST.get('q1')    # Q1: Which of the following best describes the English translation for "Abo"?
        q2 = request.POST.get('q2')    # Q2: Which of the following best describes the English translation for "Ebi"?
        q3 = request.POST.get('q3')    # Q3: Which of the following best describes the English translation for "Tani"?
        q4 = request.POST.get('q4')    # Q4: Rate the naturalness of the speech.
        q5 = request.POST.get('q5')    # Q5: Were there any pronunciation errors?
        q6 = request.POST.get('q6')    # Q6: Rate the clarity of the speech.
        q7 = request.POST.get('q7')    # Q7: Was the pacing of the speech appropriate?
        q8 = request.POST.get('q8')    # Q8: Was the tone of the voice appropriate for a proverb?
        q9 = request.POST.get('q9')    # Q9: Did you notice any background noise or artifacts?
        q10 = request.POST.get('q10')  # Q10: How would you rate the overall quality of the TTS audio?

        # Store all questions in a dictionary to easily check for completeness
        all_questions_data = {
            'q1': q1, 'q2': q2, 'q3': q3, 'q4': q4, 'q5': q5,
            'q6': q6, 'q7': q7, 'q8': q8, 'q9': q9, 'q10': q10
        }

        # Check if any required field is missing (None or empty string)
        missing_fields = [key for key, value in all_questions_data.items() if not value]

        if missing_fields:
            # If there are missing fields, re-render the form with an error message
            context = {
                'proverb': proverb,
                'proverb_rating': proverb_rating,
                'error_message': f"Please answer all questions. Missing: {', '.join(f.upper() for f in missing_fields)}.",
                **all_questions_data # Pass back submitted data to pre-populate the form
            }
            return render(request, 'proverbs/tts_rating.html', context)

        # All fields are answered, proceed with calculations and saving
        competence_score, final_rating_value = _calculate_competence_and_final_rating(
            q1, q2, q3, q4, q6, q10, proverb_rating
        )

        # Convert to int for saving where applicable.
        # These are now guaranteed to have non-empty string values due to the check above.
        q4_int = int(q4)
        q6_int = int(q6)
        q10_int = int(q10)

        # --- Save to Database ---
        current_user = request.user if request.user.is_authenticated else None

        if proverb_rating:
            models.ProverbRating.objects.create(
                proverb=proverb,
                user=current_user,
                q1=q1, q2=q2, q3=q3,
                q4=q4_int, q5=q5, q6=q6_int, q7=q7, q8=q8, q9=q9, q10=q10_int,
                competence_score=competence_score,
                final_rating=round(final_rating_value, 2)
            )
        else:
            # For GeneralRating, since all q1-q10 are now guaranteed to be answered,
            # we can directly assign q4, q5, q6, q7, q8, q9 without conditional checks.
            models.GeneralRating.objects.create(
                user=current_user,
                q1=q1, q2=q2, q3=q3,
                q4=q4_int,
                q5=q5,
                q6=q6_int,
                q7=q7,
                q8=q8,
                q9=q9,
                q10=q10_int,
                competence_score=competence_score,
                final_rating=round(final_rating_value, 2)
            )

        # Redirect back to the proverb list after successful submission
        return redirect('proverb_list')
    else:
        # Render the rating form for GET request
        context = {
            'proverb': proverb,
            'proverb_rating': proverb_rating,
        }
        return render(request, 'proverbs/tts_rating.html', context)


def generate_tts(text):
    client = Spitch(api_key=settings.SPITCH_API_KEY)
    response = client.speech.generate(
        text=text,
        language="yo",
        voice="sade"
    )
    audio_content = response.read()
    encoded_audio = base64.b64encode(audio_content).decode('utf-8')
    return encoded_audio

# V1
def tts_proverb(request, proverb_id):
    proverb = get_object_or_404(models.Proverb, pk=proverb_id)  # Fetch proverb by ID
    # encoded_audio = generate_tts(proverb.text)  # Generate TTS and get URL
    context = {'proverb': proverb}
    if not proverb.encoded_audio:
        encoded_audio = generate_tts(proverb.text)
        proverb.encoded_audio = encoded_audio
        proverb.save()
    return render(request, 'proverbs/tts_proverb.html', context)


@csrf_exempt
def generate_tts_api(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            text = data.get('text')
        except json.JSONDecodeError:
            return JsonResponse({'error': 'Invalid JSON'}, status=400)

        if not text:
            return JsonResponse({'error': 'No text provided'}, status=400)

        try:

            encoded_audio = generate_tts(text)
            return JsonResponse({"encoded_audio_url":f"data:audio/mpeg;base64,{encoded_audio}"})


        except Exception as e:
            return JsonResponse({'error': f'TTS generation failed: {str(e)}'}, status=500)
    else:
        return JsonResponse({'error': 'Invalid request method'}, status=405)


def rating_results(request, proverb_id=None):
    """
    Displays the rating results by calculating aggregate statistics and
    providing them to the template.
    """
    from django.db.models import Avg, Count
    from collections import Counter
    from operator import itemgetter

    proverb = None
    # Initialize context with defaults that match the template
    context = {
        'proverb': None,
        'total_ratings': 0,
        'recent_ratings': [],
        'avg_competence_score': None,
        'expert_percentage': 0,
        'knowledgeable_percentage': 0,
        'novice_percentage': 0,
        'avg_final_rating': 0,
        'avg_q4': 0,
        'q5_natural_percentage': 0,
        'avg_q6': 0,
        'q7_natural_percentage': 0,
        'q8_native_percentage': 0,
        'q9_preserved_percentage': 0,
        'q10_5_percentage': 0,
        'q10_4_percentage': 0,
        'q10_3_percentage': 0,
        'q10_2_percentage': 0,
        'q10_1_percentage': 0,
    }

    if proverb_id:
        # --- Proverb-specific results (using efficient DB aggregation) ---
        proverb = get_object_or_404(models.Proverb, pk=proverb_id)
        ratings = models.ProverbRating.objects.filter(proverb=proverb)
        total_ratings = ratings.count()

        context['proverb'] = proverb
        context['total_ratings'] = total_ratings

        if total_ratings > 0:
            aggregates = ratings.aggregate(
                avg_competence=Avg('competence_score'),
                avg_final=Avg('final_rating'),
                avg_q4=Avg('q4'),
                avg_q6=Avg('q6')
            )
            expert_count = ratings.filter(competence_score=3).count()
            knowledgeable_count = ratings.filter(competence_score=2).count()
            novice_count = ratings.filter(competence_score__in=[0, 1]).count()
            q5_natural_count = ratings.filter(q5='B').count()
            q7_natural_count = ratings.filter(q7='D').count()
            q8_native_count = ratings.filter(q8='C').count()
            q9_preserved_count = ratings.filter(q9='C').count()
            q10_counts = ratings.values('q10').annotate(count=Count('q10'))
            q10_map = {item['q10']: item['count'] for item in q10_counts}

            context.update({
                'avg_competence_score': aggregates['avg_competence'],
                'expert_percentage': (expert_count / total_ratings) * 100,
                'knowledgeable_percentage': (knowledgeable_count / total_ratings) * 100,
                'novice_percentage': (novice_count / total_ratings) * 100,
                'avg_final_rating': aggregates['avg_final'],
                'avg_q4': aggregates['avg_q4'],
                'q5_natural_percentage': (q5_natural_count / total_ratings) * 100,
                'avg_q6': aggregates['avg_q6'],
                'q7_natural_percentage': (q7_natural_count / total_ratings) * 100,
                'q8_native_percentage': (q8_native_count / total_ratings) * 100,
                'q9_preserved_percentage': (q9_preserved_count / total_ratings) * 100,
                'q10_5_percentage': (q10_map.get(5, 0) / total_ratings) * 100,
                'q10_4_percentage': (q10_map.get(4, 0) / total_ratings) * 100,
                'q10_3_percentage': (q10_map.get(3, 0) / total_ratings) * 100,
                'q10_2_percentage': (q10_map.get(2, 0) / total_ratings) * 100,
                'q10_1_percentage': (q10_map.get(1, 0) / total_ratings) * 100,
                'recent_ratings': ratings.order_by('-rated_at')[:5]
            })
    else:
        # --- Overall TTS System Performance (combining models in Python) ---
        # A UnionQuerySet does not support aggregation, so we fetch and process in memory.
        fields = ('competence_score', 'final_rating', 'q4', 'q5', 'q6', 'q7', 'q8', 'q9', 'q10', 'rated_at')
        general_ratings_data = list(models.GeneralRating.objects.values(*fields))
        proverb_ratings_data = list(models.ProverbRating.objects.values(*fields))
        all_ratings = general_ratings_data + proverb_ratings_data

        total_ratings = len(all_ratings)
        context['total_ratings'] = total_ratings

        if total_ratings > 0:
            # Perform calculations in Python
            avg_competence_score = sum(r['competence_score'] for r in all_ratings) / total_ratings
            avg_final_rating = sum(r['final_rating'] for r in all_ratings) / total_ratings

            q4_values = [r['q4'] for r in all_ratings if r['q4'] is not None]
            avg_q4 = sum(q4_values) / len(q4_values) if q4_values else 0

            q6_values = [r['q6'] for r in all_ratings if r['q6'] is not None]
            avg_q6 = sum(q6_values) / len(q6_values) if q6_values else 0

            expert_count = sum(1 for r in all_ratings if r['competence_score'] == 3)
            knowledgeable_count = sum(1 for r in all_ratings if r['competence_score'] == 2)
            novice_count = sum(1 for r in all_ratings if r['competence_score'] in [0, 1])

            q5_natural_count = sum(1 for r in all_ratings if r['q5'] == 'B')
            q7_natural_count = sum(1 for r in all_ratings if r['q7'] == 'D')
            q8_native_count = sum(1 for r in all_ratings if r['q8'] == 'C')
            q9_preserved_count = sum(1 for r in all_ratings if r['q9'] == 'C')

            q10_counts = Counter(r['q10'] for r in all_ratings)

            all_ratings.sort(key=itemgetter('rated_at'), reverse=True)

            context.update({
                'avg_competence_score': avg_competence_score,
                'expert_percentage': (expert_count / total_ratings) * 100,
                'knowledgeable_percentage': (knowledgeable_count / total_ratings) * 100,
                'novice_percentage': (novice_count / total_ratings) * 100,
                'avg_final_rating': avg_final_rating,
                'avg_q4': avg_q4,
                'q5_natural_percentage': (q5_natural_count / total_ratings) * 100,
                'avg_q6': avg_q6,
                'q7_natural_percentage': (q7_natural_count / total_ratings) * 100,
                'q8_native_percentage': (q8_native_count / total_ratings) * 100,
                'q9_preserved_percentage': (q9_preserved_count / total_ratings) * 100,
                'q10_5_percentage': (q10_counts.get(5, 0) / total_ratings) * 100,
                'q10_4_percentage': (q10_counts.get(4, 0) / total_ratings) * 100,
                'q10_3_percentage': (q10_counts.get(3, 0) / total_ratings) * 100,
                'q10_2_percentage': (q10_counts.get(2, 0) / total_ratings) * 100,
                'q10_1_percentage': (q10_counts.get(1, 0) / total_ratings) * 100,
                'recent_ratings': all_ratings[:5]
            })

    return render(request, 'proverbs/rating_results.html', context)
