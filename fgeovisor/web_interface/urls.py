from django.urls import path, re_path

from .views import (MapView, RegistryView, LoginView, UserAuth, LogoutView)

auth_path = [
    re_path(
        r'^auth/profile/(?P<pk>[0-9-]{0,10})$',
        UserAuth.as_view({'get': 'retrieve'}),
        name='user-profile' 
    ),
    re_path(
        r'^auth/profile/forgot-password/(?P<pk>[0-9-]{0,10}$)',
        UserAuth.as_view({'patch': 'forgot_password'}),
        name='user-forget-password'
    )
]

urlpatterns = [
    path('', MapView.as_view(), name='map'),
    path('sign-in/', RegistryView.as_view(), name='sign-in'),
    path('log-in/', LoginView.as_view(), name='log-in'),
    path('log-out/', LogoutView.as_view(), name='log-out'),
]

urlpatterns += auth_path
