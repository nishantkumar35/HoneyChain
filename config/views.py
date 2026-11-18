"""
config/views.py — Views for public pages (home, about).
"""

from django.shortcuts import render


def home_view(request):
    """Home page with feature highlights."""
    steps = [
        {
            'icon': '🐝',
            'title': 'Beekeeper Harvests',
            'description': 'A beekeeper records their honey batch details — source, quantity, harvest date, and apiary information — in HoneyChain.',
        },
        {
            'icon': '🔗',
            'title': 'Recorded on Blockchain',
            'description': 'A SHA-256 hash of the batch data is generated and permanently stored on a tamper-proof blockchain smart contract.',
        },
        {
            'icon': '📱',
            'title': 'Customer Verifies',
            'description': 'Customers scan the QR code on the jar to view full batch details and verify authenticity against the blockchain record.',
        },
    ]

    features = [
        {'icon': '🏡', 'title': 'Apiary Management', 'description': 'Manage multiple apiaries and bee colonies with health tracking.'},
        {'icon': '🍯', 'title': 'Batch Tracking', 'description': 'Create and track honey batches from harvest to packaging.'},
        {'icon': '🔗', 'title': 'Blockchain Security', 'description': 'SHA-256 hashes stored on Ethereum smart contracts via Hardhat.'},
        {'icon': '📱', 'title': 'QR Traceability', 'description': 'Auto-generated QR codes link customers to live verification pages.'},
    ]

    return render(request, 'home.html', {'steps': steps, 'features': features})


def about_view(request):
    """About page."""
    return render(request, 'about.html')

