from django.urls import path
from . import views

app_name = 'apiaries'

urlpatterns = [
    path('',              views.apiary_list,   name='list'),
    path('add/',          views.apiary_add,    name='add'),
    path('<int:pk>/',     views.apiary_detail, name='detail'),
    path('<int:pk>/edit/',   views.apiary_edit,   name='edit'),
    path('<int:pk>/delete/', views.apiary_delete, name='delete'),
]

