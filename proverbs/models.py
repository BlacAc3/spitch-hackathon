from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()

class Proverb(models.Model):
    TAG_CHOICES = [
        ('system', 'System'),
        ('user', 'User'),
    ]

    text = models.TextField(verbose_name="Yoruba Proverb Text")
    translation = models.TextField(verbose_name="English Translation", blank=True, null=True)
    audio = models.FileField(upload_to='proverb_audio/', verbose_name="Audio (TTS)", blank=True, null=True)
    tag = models.CharField(max_length=10, choices=TAG_CHOICES, default='system', verbose_name="Proverb Source")

    def __str__(self):
        text_str = str(self.text)
        return text_str[:50] + "..." if len(text_str) > 50 else text_str

    class Meta:
        verbose_name = "Proverb"
        verbose_name_plural = "Proverbs"


class ProverbRating(models.Model):
    proverb = models.ForeignKey(Proverb, on_delete=models.CASCADE, related_name='ratings')
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True) # Allow anonymous ratings

    # Defined choices to avoid repetition
    Q_CHOICES_1_3 = [('A', 'A'), ('B', 'B'), ('C', 'C'), ('D', 'D')]
    Q_CHOICES_4_6_10 = [(i, str(i)) for i in range(1, 6)]
    Q_CHOICES_5 = [('A', 'A'), ('B', 'B')]
    Q_CHOICES_7 = [('A', 'A'), ('B', 'B'), ('C', 'C'), ('D', 'D')]
    Q_CHOICES_8_9 = [('A', 'A'), ('B', 'B'), ('C', 'C')]

    # Competence Check Questions
    # Question 1: What is the correct tone for the word 'oko' in 'oko'?
    # A. Mid tone, B. High tone, C. Low tone, D. No tone
    q1 = models.CharField(max_length=1, choices=Q_CHOICES_1_3)
    # Question 2: Which of the following is NOT a Yoruba vowel?
    # A. a, B. e, C. i, D. c
    q2 = models.CharField(max_length=1, choices=Q_CHOICES_1_3)
    # Question 3: What does the proverb 'A f'ọjọ́ pẹ́ẹ́rẹ́ẹ́ f'ọjọ́ àìrí' mean?
    # A. A person who is patient will have a good outcome.
    # B. A stitch in time saves nine.
    # C. The early bird catches the worm.
    # D. Every cloud has a silver lining.
    q3 = models.CharField(max_length=1, choices=Q_CHOICES_1_3)

    # Proverb Evaluation Questions
    # 4. Naturalness: How natural does the synthesized speech sound?
    # (1: Very Unnatural, 5: Very Natural)
    q4 = models.IntegerField(choices=Q_CHOICES_4_6_10)
    # 5. Audio Quality: Is there any background noise or distortion?
    # A. Yes, B. No
    q5 = models.CharField(max_length=1, choices=Q_CHOICES_5)
    # 6. Intelligibility: How easy is it to understand the words in the synthesized speech?
    # (1: Very Difficult, 5: Very Easy)
    q6 = models.IntegerField(choices=Q_CHOICES_4_6_10)
    # 7. Pronunciation: Are there any mispronounced words?
    # A. Yes, many, B. Yes, a few, C. No, D. I'm not sure
    q7 = models.CharField(max_length=1, choices=Q_CHOICES_7)
    # 8. Tone: How well does the synthesized speech capture the tonal nature of Yoruba?
    # A. Poorly, B. Adequately, C. Excellently
    q8 = models.CharField(max_length=1, choices=Q_CHOICES_8_9)
    # 9. Rhythm and Intonation: Does the rhythm and intonation sound natural for a Yoruba speaker?
    # A. Unnatural, B. Acceptable, C. Natural
    q9 = models.CharField(max_length=1, choices=Q_CHOICES_8_9)
    # 10. Overall Quality: How would you rate the overall quality of the synthesized speech?
    # (1: Very Poor, 5: Excellent)
    q10 = models.IntegerField(choices=Q_CHOICES_4_6_10)

    # Calculated scores
    competence_score = models.IntegerField()
    final_rating = models.DecimalField(max_digits=5, decimal_places=2)

    rated_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        user_obj = self.user
        username_display = user_obj.username if user_obj else 'Anonymous'
        proverb_obj = self.proverb
        return f"Rating for Proverb {proverb_obj.pk} by {username_display}"

    class Meta:
        verbose_name = "Proverb Rating"
        verbose_name_plural = "Proverb Ratings"
        unique_together = ['proverb', 'user'] # A user can only rate a proverb once


class GeneralRating(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, null=True, blank=True) # A user can only submit one general rating

    # Competence Check Questions
    # Question 1: What is the correct tone for the word 'oko' in 'oko'?
    # A. Mid tone, B. High tone, C. Low tone, D. No tone
    q1 = models.CharField(max_length=1, choices=ProverbRating.Q_CHOICES_1_3)
    # Question 2: Which of the following is NOT a Yoruba vowel?
    # A. a, B. e, C. i, D. c
    q2 = models.CharField(max_length=1, choices=ProverbRating.Q_CHOICES_1_3)
    # Question 3: What does the proverb 'A f'ọjọ́ pẹ́ẹ́rẹ́ẹ́ f'ọjọ́ àìrí' mean?
    # A. A person who is patient will have a good outcome.
    # B. A stitch in time saves nine.
    # C. The early bird catches the worm.
    # D. Every cloud has a silver lining.
    q3 = models.CharField(max_length=1, choices=ProverbRating.Q_CHOICES_1_3)

    # Proverb Evaluation Questions (nullable for general rating)
    # 4. Naturalness: How natural does the synthesized speech sound?
    # (1: Very Unnatural, 5: Very Natural)
    q4 = models.IntegerField(choices=ProverbRating.Q_CHOICES_4_6_10, null=True, blank=True)
    # 5. Audio Quality: Is there any background noise or distortion?
    # A. Yes, B. No
    q5 = models.CharField(max_length=1, choices=ProverbRating.Q_CHOICES_5, null=True, blank=True)
    # 6. Intelligibility: How easy is it to understand the words in the synthesized speech?
    # (1: Very Difficult, 5: Very Easy)
    q6 = models.IntegerField(choices=ProverbRating.Q_CHOICES_4_6_10, null=True, blank=True)
    # 7. Pronunciation: Are there any mispronounced words?
    # A. Yes, many, B. Yes, a few, C. No, D. I'm not sure
    q7 = models.CharField(max_length=1, choices=ProverbRating.Q_CHOICES_7, null=True, blank=True)
    # 8. Tone: How well does the synthesized speech capture the tonal nature of Yoruba?
    # A. Poorly, B. Adequately, C. Excellently
    q8 = models.CharField(max_length=1, choices=ProverbRating.Q_CHOICES_8_9, null=True, blank=True)
    # 9. Rhythm and Intonation: Does the rhythm and intonation sound natural for a Yoruba speaker?
    # A. Unnatural, B. Acceptable, C. Natural
    q9 = models.CharField(max_length=1, choices=ProverbRating.Q_CHOICES_8_9, null=True, blank=True)
    # 10. Overall Quality: How would you rate the overall quality of the synthesized speech?
    # (1: Very Poor, 5: Excellent)
    q10 = models.IntegerField(choices=ProverbRating.Q_CHOICES_4_6_10) # Q10 is always required for overall impression.

    # Calculated scores
    competence_score = models.IntegerField()
    final_rating = models.DecimalField(max_digits=5, decimal_places=2)

    rated_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        user_obj = self.user
        username_display = user_obj.username if user_obj else 'Anonymous'
        return f"General Rating by {username_display}"

    class Meta:
        verbose_name = "General Rating"
        verbose_name_plural = "General Ratings"
