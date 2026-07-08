from django.urls import path
from . import views

urlpatterns = [
    path("", views.login_view, name="login"),
    path("dashboard/", views.dashboard_view, name="dashboard"),
    path("logout/", views.logout_view, name="logout"),
    path("acesso-negado/", views.acesso_negado, name="acesso_negado"),
]
