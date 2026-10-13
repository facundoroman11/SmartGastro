from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [
    path('', views.inventario, name='inventario'),
    path('eliminar/<int:id>/', views.eliminar_producto, name='eliminar_producto'),
    path('login/', auth_views.LoginView.as_view(template_name='registration/login.html'), name='login'),
    path('logout/', views.salir, name='logout'),
]