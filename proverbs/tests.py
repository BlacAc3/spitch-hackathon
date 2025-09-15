from django.test import TestCase, Client
from django.urls import reverse
from .models import Proverb, ProverbRating, GeneralRating
from django.contrib.auth.models import User

class RatingResultsViewTests(TestCase):
    def setUp(self):
        # Create a test client
        self.client = Client()
        # Create a test user
        self.user = User.objects.create_user(username='testuser', password='password')
        self.client.login(username='testuser', password='password')

        # Create a test proverb
        self.proverb = Proverb.objects.create(text="Test Proverb", translation="Test Translation")

    def test_rating_results_general_view(self):
        # Create some general ratings for testing
        GeneralRating.objects.create(
            user=self.user,
            q1='B', q2='B', q3='D', q4=5, q6=5, q10=5,
            competence_score=3, final_rating=5.0
        )
        GeneralRating.objects.create(
            user=User.objects.create_user(username='testuser2', password='password'),
            q1='A', q2='B', q3='C', q4=3, q6=4, q10=3,
            competence_score=2, final_rating=3.3
        )

        url = reverse('rating_results_general')
        response = self.client.get(url)

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'proverbs/rating_results.html')
        self.assertTrue('avg_competence_score' in response.context)
        # Add more specific assertions here to validate the results data

    def test_rating_results_proverb_view(self):
        # Create some proverb ratings for testing
        ProverbRating.objects.create(
            proverb=self.proverb, user=self.user,
            q1='B', q2='B', q3='D', q4=5, q6=5, q10=5,
            competence_score=3, final_rating=5.0
        )
        ProverbRating.objects.create(
            proverb=self.proverb, user=User.objects.create_user(username='testuser2', password='password'),
            q1='A', q2='B', q3='C', q4=3, q6=4, q10=3,
            competence_score=2, final_rating=3.3
        )

        url = reverse('rating_results_proverb', args=[self.proverb.id])
        response = self.client.get(url)

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'proverbs/rating_results.html')
        self.assertTrue('proverb' in response.context)
        self.assertEqual(response.context['proverb'], self.proverb)
        self.assertTrue('avg_competence_score' in response.context)
        # Add more specific assertions here to validate the results data

    # Add tests for rating calculations (example)
    def test_rating_calculations(self):
        # Test competence score
        # Test Final rating value
        pass  # Implement assertions based on sample data

    def test_anonymous_rating_results(self):
         # Test to ensure it works for anonymous users.
         self.client.logout()
         url = reverse('rating_results_general')
         response = self.client.get(url)
         self.assertEqual(response.status_code, 200)
         self.assertTemplateUsed(response, 'proverbs/rating_results.html')
