from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.urls import reverse
from apiaries.models import Apiary
from honey.models import HoneyBatch
from blockchain.utils import generate_batch_hash
from datetime import date
from decimal import Decimal


class HoneyBatchTestCase(TestCase):
    def setUp(self):
        self.user1 = User.objects.create_user('keeper1', 'k1@test.com', 'Pass@123', first_name='John', last_name='Doe')
        self.user2 = User.objects.create_user('keeper2', 'k2@test.com', 'Pass@123')
        self.client1 = Client()
        self.client1.force_login(self.user1)

        self.apiary1 = Apiary.objects.create(
            beekeeper=self.user1,
            name='Alpha Apiary',
            location='Punjab Fields'
        )

        self.batch = HoneyBatch.objects.create(
            beekeeper=self.user1,
            apiary=self.apiary1,
            honey_source='Mustard',
            harvest_date=date(2024, 5, 10),
            quantity=Decimal('35.50'),
            location='Punjab Fields',
            status='Harvested'
        )
        self.batch.data_hash = generate_batch_hash(self.batch)
        self.batch.save()

    def test_batch_auto_generates_id(self):
        self.assertTrue(self.batch.batch_id.startswith('HC-'))
        self.assertGreater(len(self.batch.batch_id), 8)

    def test_sha256_hash_deterministic(self):
        """Recomputing hash on identical batch data must yield exact same hex string."""
        hash1 = generate_batch_hash(self.batch)
        hash2 = generate_batch_hash(self.batch)
        self.assertEqual(hash1, hash2)
        self.assertEqual(len(hash1), 64)

    def test_hash_changes_if_data_modified(self):
        original_hash = self.batch.data_hash
        self.batch.quantity = Decimal('40.00')
        new_hash = generate_batch_hash(self.batch)
        self.assertNotEqual(original_hash, new_hash)

    def test_blockchain_registered_batch_locked_from_edit(self):
        """Batches registered on the blockchain cannot be edited."""
        self.batch.is_registered_on_blockchain = True
        self.batch.save()

        response = self.client1.post(reverse('honey:edit', kwargs={'pk': self.batch.pk}), {
            'apiary': self.apiary1.pk,
            'honey_source': 'Wildflower',
            'harvest_date': '2024-05-10',
            'quantity': '50.00',
            'location': 'Punjab Fields',
            'status': 'Processing'
        }, follow=True)

        self.batch.refresh_from_db()
        self.assertEqual(self.batch.honey_source, 'Mustard')  # did not change

