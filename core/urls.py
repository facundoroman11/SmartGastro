from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [
    path("", views.inventario, name="inventario"),
    path("ventas/", views.ventas, name="ventas"),
    path("eliminar/<int:id>/", views.eliminar_producto, name="eliminar_producto"),
    path("editar/<int:id>/", views.editar_producto, name="editar_producto"),
    path(
        "login/",
        auth_views.LoginView.as_view(template_name="registration/login.html"),
        name="login",
    ),
    path("logout/", views.salir, name="salir"),
    path("logout-alias/", views.salir, name="logout"),
]
