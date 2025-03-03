from django.urls import path, re_path

from .views import (MapView, RegistryView, LoginView, UserAuthViewSet,
                    LogoutView)

auth_path = [
    re_path(r'^auth/profile$',
            UserAuthViewSet.as_view({'get': 'retrieve'}),
            name='user-profile'),
    re_path(r'^auth/profile/forgot-password$',
            UserAuthViewSet.as_view({'patch': 'forgot_password'}),
            name='user-forget-password'),
    re_path(r'^auth/register$',
            UserAuthViewSet.as_view({'post': 'create'}),
            name='user-register'),
    re_path(
        r'^auth/login$',
        # we also can make retrieve as auth func
        UserAuthViewSet.as_view({'post': 'authenticate'}),
        name='user-login'),
    re_path(
        r'^auth/logout$',
        UserAuthViewSet.as_view({'post': 'logout'}),
        name='user-logout'
    )
]

urlpatterns = [
    path('', MapView.as_view(), name='map'),
    path('sign-in/', RegistryView.as_view(), name='sign-in'),
    path('log-in/', LoginView.as_view(), name='log-in'),
    path('log-out/', LogoutView.as_view(), name='log-out'),
]

urlpatterns += auth_path
