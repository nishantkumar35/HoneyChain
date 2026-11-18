from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.urls import reverse
from .models import Apiary


class ApiaryTestCase(TestCase):
    def setUp(self):
        self.user1 = User.objects.create_user('keeper1', 'k1@test.com', 'Pass@123')
        self.user2 = User.objects.create_user('keeper2', 'k2@test.com', 'Pass@123')
        self.client1 = Client()
        self.client1.force_login(self.user1)
        self.client2 = Client()
        self.client2.force_login(self.user2)

        self.apiary1 = Apiary.objects.create(
            beekeeper=self.user1,
            name='Alpha Apiary',
            location='Punjab Fields',
            description='Wildflower rich location'
        )

    def test_apiary_list_filters_by_user(self):
        """User only sees their own apiaries."""
        response = self.client1.get(reverse('apiaries:list'))
        self.assertContains(response, 'Alpha Apiary')

        response2 = self.client2.get(reverse('apiaries:list'))
        self.assertNotContains(response2, 'Alpha Apiary')

    def test_create_apiary(self):
        """Authenticated user can create apiary."""
        response = self.client1.post(reverse('apiaries:add'), {
            'name': 'Beta Apiary',
            'location': 'Himachal Valley',
            'description': 'Mountain flowers'
        }, follow=True)
        self.assertRedirects(response, reverse('apiaries:list'))
        self.assertTrue(Apiary.objects.filter(name='Beta Apiary', beekeeper=self.user1).exists())

    def test_unauthorized_edit_forbidden(self):
        """User2 cannot edit user1's apiary (returns 403 PermissionDenied)."""
        response = self.client2.post(reverse('apiaries:edit', kwargs={'pk': self.apiary1.pk}), {
            'name': 'Hacked Apiary',
            'location': 'Nowhere',
            'description': 'Malicious edit'
        })
        self.assertEqual(response.status_code, 403)
        self.apiary1.refresh_from_db()
        self.assertEqual(self.apiary1.name, 'Alpha Apiary')

