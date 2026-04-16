from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import AuthLoginApi, AuthLogoutApi, AuthMeApi, PatronBlockViewSet, PatronViewSet, UserViewSet

router = DefaultRouter()
router.register('operators', UserViewSet, basename='users-operator')
router.register('patrons', PatronViewSet, basename='users-patron')
router.register('patron-blocks', PatronBlockViewSet, basename='users-patron-block')

urlpatterns = [
    path('auth/login/', AuthLoginApi.as_view(), name='auth-login'),
    path('auth/me/', AuthMeApi.as_view(), name='auth-me'),
    path('auth/logout/', AuthLogoutApi.as_view(), name='auth-logout'),
    path('', include(router.urls)),
]
