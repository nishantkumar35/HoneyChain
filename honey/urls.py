from django.urls import path
from . import views

app_name = 'honey'

urlpatterns = [
    path('',                             views.batch_list,               name='list'),
    path('create/',                      views.batch_create,             name='create'),
    path('<int:pk>/',                    views.batch_detail,             name='detail'),
    path('<int:pk>/edit/',               views.batch_edit,               name='edit'),
    path('<int:pk>/delete/',             views.batch_delete,             name='delete'),
    path('<int:pk>/register-blockchain/', views.batch_register_blockchain, name='register_blockchain'),
    path('<int:pk>/verify-blockchain/',   views.batch_verify_blockchain,   name='verify_blockchain'),
]

