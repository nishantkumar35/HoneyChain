"""
seed_data.py — Populates HoneyChain with realistic Indian beekeeping data.

Usage:
    python manage.py seed_data
"""

from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import date, timedelta
from decimal import Decimal
import hashlib

from apiaries.models import Apiary
from colonies.models import BeeColony
from honey.models import HoneyBatch, BlockchainRecord
from blockchain.utils import generate_batch_hash, generate_qr_code
from blockchain.services import register_batch_on_blockchain
from blockchain.contract import is_blockchain_available


class Command(BaseCommand):
    help = 'Seeds realistic Indian beekeepers, apiaries, colonies, and honey batches.'

    def handle(self, *args, **options):
        self.stdout.write(self.style.NOTICE("=== Seeding Indian Beekeeping Data into HoneyChain ==="))

        # =====================================================================
        # 1. Beekeepers (User + BeekeeperProfile)
        # =====================================================================
        beekeepers_data = [
            {
                'username':   'ramesh_kumar',
                'first_name': 'Ramesh',
                'last_name':  'Kumar',
                'email':      'ramesh.kumar@himalayanhoney.in',
                'phone':      '+91 98160 12345',
                'address':    'Village Shahpur, Kangra Valley, Himachal Pradesh - 176206',
            },
            {
                'username':   'gurpreet_singh',
                'first_name': 'Gurpreet',
                'last_name':  'Singh',
                'email':      'gurpreet@punjabhoney.co.in',
                'phone':      '+91 98722 54321',
                'address':    'Majitha Road Farm, Amritsar, Punjab - 143001',
            },
            {
                'username':   'priya_sharma',
                'first_name': 'Priya',
                'last_name':  'Sharma',
                'email':      'priya@pahadihoney.org',
                'phone':      '+91 94120 98765',
                'address':    'Bhimtal Valley, Nainital, Uttarakhand - 263136',
            },
        ]

        beekeepers = {}
        for data in beekeepers_data:
            user, created = User.objects.get_or_create(
                username=data['username'],
                defaults={
                    'first_name': data['first_name'],
                    'last_name':  data['last_name'],
                    'email':      data['email'],
                }
            )
            user.set_password('Password@123')
            user.save()

            profile = user.beekeeper_profile
            profile.phone = data['phone']
            profile.address = data['address']
            profile.save()

            beekeepers[data['username']] = user
            status_text = "Created" if created else "Updated"
            self.stdout.write(f"  [USER] {status_text} beekeeper: {user.get_full_name()} ({user.username})")

        # =====================================================================
        # 2. Apiaries across Indian states
        # =====================================================================
        apiaries_data = [
            {
                'beekeeper':   beekeepers['ramesh_kumar'],
                'name':        'Dhauladhar Alpine Apiary',
                'location':    'Kangra Valley, Dharamshala, Himachal Pradesh',
                'description': 'High altitude wild floral flora apiary nestled in the foothills of the Dhauladhar ranges. Specialises in raw Multifloral and Wild Acacia honey.',
            },
            {
                'beekeeper':   beekeepers['ramesh_kumar'],
                'name':        'Kullu Apple Blossom Apiary',
                'location':    'Naggar Village, Kullu Valley, Himachal Pradesh',
                'description': 'Seasonal migratory apiary placed in apple and plum orchards during early spring pollination.',
            },
            {
                'beekeeper':   beekeepers['gurpreet_singh'],
                'name':        'Golden Fields Mustard Apiary',
                'location':    'Majitha Bypass, Amritsar, Punjab',
                'description': 'Extensive winter mustard (Sarson) apiary. Bees forage across organic yellow mustard fields producing quick-crystallizing creamy honey.',
            },
            {
                'beekeeper':   beekeepers['gurpreet_singh'],
                'name':        'Doaba Eucalyptus Farm',
                'location':    'Dasuya Tehsil, Hoshiarpur, Punjab',
                'description': 'Lush eucalyptus and shisham plantation apiary providing therapeutic, light-amber aromatic honey.',
            },
            {
                'beekeeper':   beekeepers['priya_sharma'],
                'name':        'Nainital Forest Flora Apiary',
                'location':    'Bhimtal Forest Range, Nainital, Uttarakhand',
                'description': 'Pesticide-free oak and rhododendron forest reserve apiary. Produces rare dark forest medicinal honey.',
            },
        ]

        apiaries = []
        for data in apiaries_data:
            apiary, _ = Apiary.objects.get_or_create(
                beekeeper=data['beekeeper'],
                name=data['name'],
                defaults={
                    'location':    data['location'],
                    'description': data['description'],
                }
            )
            apiaries.append(apiary)
            self.stdout.write(f"  [APIARY] {apiary.name} ({apiary.location})")

        # =====================================================================
        # 3. Bee Colonies with Indian / commercial subspecies
        # =====================================================================
        colonies_data = [
            # Ramesh Kumar's colonies
            {
                'apiary':             apiaries[0],
                'colony_name':        'Dhauladhar Hive Alpha (DH-01)',
                'colony_type':        'Italian',
                'establishment_date': date(2023, 4, 10),
                'health_status':      'Excellent',
            },
            {
                'apiary':             apiaries[0],
                'colony_name':        'Kangra Desi Hive (KD-02)',
                'colony_type':        'Indian',
                'establishment_date': date(2023, 6, 15),
                'health_status':      'Good',
            },
            {
                'apiary':             apiaries[1],
                'colony_name':        'Naggar Apple Hive (NA-01)',
                'colony_type':        'Italian',
                'establishment_date': date(2024, 2, 20),
                'health_status':      'Excellent',
            },
            # Gurpreet Singh's colonies
            {
                'apiary':             apiaries[2],
                'colony_name':        'Sarson Queen Hive (SQ-101)',
                'colony_type':        'Italian',
                'establishment_date': date(2022, 10, 5),
                'health_status':      'Excellent',
            },
            {
                'apiary':             apiaries[2],
                'colony_name':        'Majitha Gold Hive (MG-102)',
                'colony_type':        'Italian',
                'establishment_date': date(2023, 11, 1),
                'health_status':      'Good',
            },
            {
                'apiary':             apiaries[3],
                'colony_name':        'Hoshiarpur Timber Hive (HT-01)',
                'colony_type':        'Italian',
                'establishment_date': date(2024, 1, 12),
                'health_status':      'Fair',
            },
            # Priya Sharma's colonies
            {
                'apiary':             apiaries[4],
                'colony_name':        'Kumaon Mountain Hive (KM-01)',
                'colony_type':        'Indian',
                'establishment_date': date(2023, 5, 18),
                'health_status':      'Excellent',
            },
            {
                'apiary':             apiaries[4],
                'colony_name':        'Bhimtal Forest Hive (BF-02)',
                'colony_type':        'Indian',
                'establishment_date': date(2023, 8, 22),
                'health_status':      'Good',
            },
        ]

        for data in colonies_data:
            colony, _ = BeeColony.objects.get_or_create(
                apiary=data['apiary'],
                colony_name=data['colony_name'],
                defaults={
                    'colony_type':        data['colony_type'],
                    'establishment_date': data['establishment_date'],
                    'health_status':      data['health_status'],
                }
            )
            self.stdout.write(f"  [COLONY] {colony.colony_name} ({colony.colony_type} - {colony.health_status})")

        # =====================================================================
        # 4. Honey Batches (with Indian honey varieties)
        # =====================================================================
        batches_data = [
            {
                'batch_id':     'HC-2026-IND001',
                'beekeeper':    beekeepers['gurpreet_singh'],
                'apiary':       apiaries[2],
                'honey_source': 'Mustard',
                'harvest_date': date(2026, 2, 14),
                'quantity':     Decimal('65.50'),
                'location':     'Majitha Bypass, Amritsar, Punjab',
                'status':       'Available',
                'on_chain':     True,
            },
            {
                'batch_id':     'HC-2026-IND002',
                'beekeeper':    beekeepers['ramesh_kumar'],
                'apiary':       apiaries[0],
                'honey_source': 'Wildflower',
                'harvest_date': date(2026, 4, 18),
                'quantity':     Decimal('42.00'),
                'location':     'Kangra Valley, Dharamshala, Himachal Pradesh',
                'status':       'Available',
                'on_chain':     True,
            },
            {
                'batch_id':     'HC-2026-IND003',
                'beekeeper':    beekeepers['priya_sharma'],
                'apiary':       apiaries[4],
                'honey_source': 'Multifloral',
                'harvest_date': date(2026, 5, 25),
                'quantity':     Decimal('38.25'),
                'location':     'Bhimtal Forest Range, Nainital, Uttarakhand',
                'status':       'Packaged',
                'on_chain':     True,
            },
            {
                'batch_id':     'HC-2026-IND004',
                'beekeeper':    beekeepers['ramesh_kumar'],
                'apiary':       apiaries[1],
                'honey_source': 'Acacia',
                'harvest_date': date(2026, 6, 10),
                'quantity':     Decimal('28.00'),
                'location':     'Naggar, Kullu Valley, Himachal Pradesh',
                'status':       'Processing',
                'on_chain':     False,
            },
            {
                'batch_id':     'HC-2026-IND005',
                'beekeeper':    beekeepers['gurpreet_singh'],
                'apiary':       apiaries[3],
                'honey_source': 'Eucalyptus',
                'harvest_date': date(2026, 7, 2),
                'quantity':     Decimal('85.00'),
                'location':     'Dasuya, Hoshiarpur, Punjab',
                'status':       'Harvested',
                'on_chain':     False,
            },
        ]

        blockchain_online = is_blockchain_available()
        if blockchain_online:
            self.stdout.write(self.style.SUCCESS("  [BLOCKCHAIN] Node is online! Registering on-chain batches..."))
        else:
            self.stdout.write(self.style.WARNING("  [BLOCKCHAIN] Node offline. Seeding realistic demo records."))

        for data in batches_data:
            batch, created = HoneyBatch.objects.get_or_create(
                batch_id=data['batch_id'],
                defaults={
                    'beekeeper':    data['beekeeper'],
                    'apiary':       data['apiary'],
                    'honey_source': data['honey_source'],
                    'harvest_date': data['harvest_date'],
                    'quantity':     data['quantity'],
                    'location':     data['location'],
                    'status':       data['status'],
                }
            )

            # Generate SHA-256 hash & QR code
            batch.data_hash = generate_batch_hash(batch)
            generate_qr_code(batch)
            batch.save()

            if data['on_chain']:
                if blockchain_online:
                    result = register_batch_on_blockchain(batch)
                    if result['success']:
                        self.stdout.write(self.style.SUCCESS(
                            f"  [BATCH] {batch.batch_id} ({batch.honey_source}) on-chain! TX: {result['tx_hash'][:16]}..."
                        ))
                    else:
                        self.stdout.write(self.style.WARNING(
                            f"  [BATCH] {batch.batch_id}: note: {result['error']}"
                        ))
                else:
                    simulated_tx = "0x" + hashlib.sha256(f"{batch.batch_id}_tx".encode()).hexdigest()
                    BlockchainRecord.objects.update_or_create(
                        honey_batch=batch,
                        defaults={
                            'transaction_hash':   simulated_tx,
                            'block_number':       18442907 + batch.pk,
                            'blockchain_hash':    f"0x{batch.data_hash}",
                            'verification_status': 'Verified',
                            'registered_at':      timezone.now() - timedelta(days=2),
                        }
                    )
                    batch.is_registered_on_blockchain = True
                    batch.save(update_fields=['is_registered_on_blockchain'])
                    self.stdout.write(self.style.SUCCESS(
                        f"  [BATCH] {batch.batch_id} ({batch.honey_source}) Verified (TX: {simulated_tx[:16]}...)"
                    ))
            else:
                self.stdout.write(f"  [BATCH] {batch.batch_id} ({batch.honey_source}) seeded as {batch.status}")

        self.stdout.write(self.style.SUCCESS("\n[SUCCESS] Successfully seeded Indian beekeeping demo data!"))
        self.stdout.write(self.style.SUCCESS("---------------------------------------------------------"))
        self.stdout.write("  Demo Accounts (Password: Password@123):")
        self.stdout.write("     - ramesh_kumar    (Kangra Valley, HP - 2 Apiaries, Wildflower & Acacia)")
        self.stdout.write("     - gurpreet_singh  (Amritsar, Punjab - 2 Apiaries, Mustard & Eucalyptus)")
        self.stdout.write("     - priya_sharma    (Nainital, Uttarakhand - 1 Apiary, Multifloral Forest)")
        self.stdout.write("     - admin           (Admin user - Admin@1234)")
        self.stdout.write("  Demo Batches to verify:")
        self.stdout.write("     - HC-2026-IND001  (Mustard Honey, Amritsar - Verified)")
        self.stdout.write("     - HC-2026-IND002  (Wildflower Honey, Kangra - Verified)")
        self.stdout.write("     - HC-2026-IND003  (Multifloral Honey, Nainital - Verified)")
        self.stdout.write("     - HC-2026-IND004  (Acacia Honey, Kullu - Processing, Pending)")
        self.stdout.write("     - HC-2026-IND005  (Eucalyptus Honey, Doaba - Harvested, Pending)")
        self.stdout.write("---------------------------------------------------------\n")
