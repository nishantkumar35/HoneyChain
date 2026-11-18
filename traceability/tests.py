from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.urls import reverse
from apiaries.models import Apiary
from honey.models import HoneyBatch
from datetime import date
from decimal import Decimal


class TraceabilityTestCase(TestCase):
    def setUp(self):
        self.client = Client()
        self.beekeeper = User.objects.create_user(
            'honest_beekeeper', 'beekeeper@example.com', 'Pass@123',
            first_name='Ramesh', last_name='Kumar'
        )
        self.apiary = Apiary.objects.create(
            beekeeper=self.beekeeper,
            name='Golden Valley Farm',
            location='Kashmir'
        )
        self.batch = HoneyBatch.objects.create(
            beekeeper=self.beekeeper,
            apiary=self.apiary,
            honey_source='Wildflower',
            harvest_date=date(2024, 6, 20),
            quantity=Decimal('50.00'),
            location='Kashmir High Altitude',
            status='Packaged'
        )

    def test_public_verify_page_accessible_without_login(self):
        """Customers can verify batch authenticity without logging in."""
        url = reverse('traceability:verify', kwargs={'batch_id': self.batch.batch_id})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.batch.batch_id)
        self.assertContains(response, 'Ramesh Kumar')
        self.assertContains(response, 'Golden Valley Farm')
        self.assertContains(response, 'Wildflower')
        self.assertNotContains(response, 'beekeeper@example.com')  # No private email exposed

    def test_batch_search_redirects_to_verify(self):
        response = self.client.get(reverse('traceability:search'), {'batch_id': self.batch.batch_id})
        self.assertRedirects(response, reverse('traceability:verify', kwargs={'batch_id': self.batch.batch_id}))

    def test_nonexistent_batch_returns_404(self):
        url = reverse('traceability:verify', kwargs={'batch_id': 'HC-9999-NONEXIST'})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)

