
# УРЛЫ ПРИЛОЖУХИ

from django.urls import path
from . import views

urlpatterns = [
    path('', views.MapView.as_view(), name='map'),
    path('sign-in/', views.RegistrationView.as_view(), name='sign-in'),
    path('log-in/', views.LoginView.as_view(), name='log-in'),
    path('log-out/', views.LogoutView.as_view(), name='log-out'),
    path("get-events/", views.get_calendar_events, name="get_calendar_events"),
]
