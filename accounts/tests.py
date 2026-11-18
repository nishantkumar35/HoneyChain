from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.urls import reverse
from .models import BeekeeperProfile


class AccountsTestCase(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username='testbeekeeper',
            password='TestPassword@123',
            email='beekeeper@example.com',
            first_name='John',
            last_name='Doe'
        )

    def test_profile_auto_created(self):
        """BeekeeperProfile should be auto-created on User creation via post_save signal."""
        self.assertTrue(hasattr(self.user, 'beekeeper_profile'))
        self.assertIsInstance(self.user.beekeeper_profile, BeekeeperProfile)

    def test_login_and_logout(self):
        """Test login and secure POST-only logout."""
        # GET login
        response = self.client.get(reverse('accounts:login'))
        self.assertEqual(response.status_code, 200)

        # POST valid credentials
        response = self.client.post(reverse('accounts:login'), {
            'username': 'testbeekeeper',
            'password': 'TestPassword@123'
        }, follow=True)
        self.assertRedirects(response, reverse('accounts:dashboard'))
        self.assertTrue(response.context['user'].is_authenticated)

        # POST logout
        response = self.client.post(reverse('accounts:logout'), follow=True)
        self.assertRedirects(response, reverse('home'))
        self.assertFalse(response.context['user'].is_authenticated)

    def test_dashboard_login_required(self):
        """Unauthenticated user cannot access dashboard."""
        response = self.client.get(reverse('accounts:dashboard'))
        self.assertEqual(response.status_code, 302)
        self.assertIn('/accounts/login/', response.url)

    def test_registration(self):
        """Test new user registration."""
        response = self.client.post(reverse('accounts:register'), {
            'username': 'newuser123',
            'first_name': 'Alice',
            'last_name': 'Smith',
            'email': 'alice@example.com',
            'phone': '9876543210',
            'address': 'Farm Road 4',
            'password1': 'SecurePass@123',
            'password2': 'SecurePass@123'
        }, follow=True)
        self.assertRedirects(response, reverse('accounts:dashboard'))
        new_user = User.objects.get(username='newuser123')
        self.assertEqual(new_user.beekeeper_profile.phone, '9876543210')

