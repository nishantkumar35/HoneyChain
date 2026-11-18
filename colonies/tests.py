from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.urls import reverse
from apiaries.models import Apiary
from .models import BeeColony
from datetime import date


class ColonyTestCase(TestCase):
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
            location='Punjab Fields'
        )

        self.colony1 = BeeColony.objects.create(
            apiary=self.apiary1,
            colony_name='Queen Victoria 01',
            colony_type='Italian',
            establishment_date=date(2024, 3, 1),
            health_status='Excellent'
        )

    def test_colony_list_shows_owned_colonies(self):
        response = self.client1.get(reverse('colonies:list'))
        self.assertContains(response, 'Queen Victoria 01')

        response2 = self.client2.get(reverse('colonies:list'))
        self.assertNotContains(response2, 'Queen Victoria 01')

    def test_create_colony(self):
        response = self.client1.post(reverse('colonies:add'), {
            'apiary': self.apiary1.pk,
            'colony_name': 'Hive Beta',
            'colony_type': 'Carniolan',
            'establishment_date': '2024-04-15',
            'health_status': 'Good'
        }, follow=True)
        self.assertRedirects(response, reverse('colonies:list'))
        self.assertTrue(BeeColony.objects.filter(colony_name='Hive Beta').exists())

    def test_unauthorized_delete_forbidden(self):
        response = self.client2.post(reverse('colonies:delete', kwargs={'pk': self.colony1.pk}))
        self.assertEqual(response.status_code, 403)
        self.assertTrue(BeeColony.objects.filter(pk=self.colony1.pk).exists())

