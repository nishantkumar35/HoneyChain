from django.urls import path
from . import views

app_name = 'colonies'

urlpatterns = [
    path('',                 views.colony_list,   name='list'),
    path('add/',             views.colony_add,    name='add'),
    path('<int:pk>/edit/',   views.colony_edit,   name='edit'),
    path('<int:pk>/delete/', views.colony_delete, name='delete'),
]

