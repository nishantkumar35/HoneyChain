from django.urls import path
from . import views

app_name = 'traceability'

urlpatterns = [
    path('',                      views.batch_search,       name='search'),
    path('<str:batch_id>/',       views.batch_verify_public, name='verify'),
]

