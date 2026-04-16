from django.urls import path

from .views import (
    PatronLoginApi,
    PatronMeApi,
    PatronMyLoansApi,
    PatronMyReservationsApi,
    PatronRenewLoanApi,
    PatronSetPasswordApi,
)

urlpatterns = [
    path('auth/login/', PatronLoginApi.as_view(), name='portal-auth-login'),
    path('auth/set-password/', PatronSetPasswordApi.as_view(), name='portal-auth-set-password'),
    path('auth/me/', PatronMeApi.as_view(), name='portal-auth-me'),
    path('my/loans/', PatronMyLoansApi.as_view(), name='portal-my-loans'),
    path('my/reservations/', PatronMyReservationsApi.as_view(), name='portal-my-reservations'),
    path('my/loans/<uuid:loan_id>/renew/', PatronRenewLoanApi.as_view(), name='portal-loan-renew'),
]
