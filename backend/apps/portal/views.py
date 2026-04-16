from django.contrib.auth import authenticate
from rest_framework import status
from rest_framework.authtoken.models import Token
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.circulation.models import Loan, Reservation
from apps.users.models import Patron, User

from .permissions import IsPatron
from .serializers import (
    PatronLoginSerializer,
    PatronMeSerializer,
    PatronPortalLoanSerializer,
    PatronPortalReservationSerializer,
    PatronSetPasswordSerializer,
)


class PatronLoginApi(APIView):
    authentication_classes = []
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = PatronLoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        registration_code = serializer.validated_data['registration_code']
        password = serializer.validated_data['password']

        try:
            patron = Patron.objects.select_related('user').get(registration_code=registration_code)
        except Patron.DoesNotExist:
            return Response({'detail': 'Matricula ou senha invalida.'}, status=status.HTTP_400_BAD_REQUEST)

        if patron.status == Patron.Status.INACTIVE:
            return Response({'detail': 'Cadastro inativo. Procure a biblioteca.'}, status=status.HTTP_403_FORBIDDEN)

        # Garante que o Patron tenha um User vinculado
        if patron.user is None:
            email = patron.email or f'{registration_code}@portal.biblioteca.local'
            user, created = User.objects.get_or_create(
                email=email,
                defaults={'role': 'assistant', 'is_active': True},
            )
            if created:
                user.set_unusable_password()
                user.save(update_fields=['password'])
            patron.user = user
            patron.save(update_fields=['user', 'updated_at'])

        user = patron.user

        # Tenta autenticar pela senha do User Django
        authenticated = authenticate(request, email=user.email, password=password)
        if authenticated is None:
            # Se o usuário não tem senha configurada, primeira vez — senha = registration_code por padrão
            if not user.has_usable_password():
                return Response(
                    {'detail': 'Conta ainda sem senha definida. Use o endpoint /portal/auth/set-password/ para criar sua senha.', 'must_set_password': True},
                    status=status.HTTP_403_FORBIDDEN,
                )
            return Response({'detail': 'Matricula ou senha invalida.'}, status=status.HTTP_400_BAD_REQUEST)

        token, _ = Token.objects.get_or_create(user=user)
        return Response({
            'token': token.key,
            'patron': PatronMeSerializer(patron).data,
        })


class PatronSetPasswordApi(APIView):
    authentication_classes = []
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = PatronSetPasswordSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        registration_code = serializer.validated_data['registration_code']
        new_password = serializer.validated_data['password']

        try:
            patron = Patron.objects.select_related('user').get(registration_code=registration_code)
        except Patron.DoesNotExist:
            return Response({'detail': 'Matricula nao encontrada.'}, status=status.HTTP_400_BAD_REQUEST)

        if patron.status == Patron.Status.INACTIVE:
            return Response({'detail': 'Cadastro inativo.'}, status=status.HTTP_403_FORBIDDEN)

        # Garante User vinculado
        if patron.user is None:
            email = patron.email or f'{registration_code}@portal.biblioteca.local'
            user, created = User.objects.get_or_create(
                email=email,
                defaults={'role': 'assistant', 'is_active': True},
            )
            patron.user = user
            patron.save(update_fields=['user', 'updated_at'])
        else:
            user = patron.user

        user.set_password(new_password)
        user.save(update_fields=['password'])

        token, _ = Token.objects.get_or_create(user=user)
        return Response({
            'token': token.key,
            'patron': PatronMeSerializer(patron).data,
        })


class PatronMeApi(APIView):
    permission_classes = [IsPatron]

    def get(self, request):
        patron = request.user.patron_profile
        return Response(PatronMeSerializer(patron).data)


class PatronMyLoansApi(APIView):
    permission_classes = [IsPatron]

    def get(self, request):
        patron = request.user.patron_profile
        loans = (
            Loan.objects
            .select_related('item_copy__bibliographic_record', 'item_copy__library_branch')
            .filter(patron=patron)
            .order_by('-loaned_at')
        )
        return Response(PatronPortalLoanSerializer(loans, many=True).data)


class PatronMyReservationsApi(APIView):
    permission_classes = [IsPatron]

    def get(self, request):
        patron = request.user.patron_profile
        reservations = (
            Reservation.objects
            .select_related('bibliographic_record', 'pickup_branch', 'fulfilled_item_copy')
            .filter(patron=patron)
            .order_by('-created_at')
        )
        return Response(PatronPortalReservationSerializer(reservations, many=True).data)


class PatronRenewLoanApi(APIView):
    permission_classes = [IsPatron]

    def post(self, request, loan_id):
        patron = request.user.patron_profile
        try:
            loan = Loan.objects.select_related('item_copy__bibliographic_record').get(
                id=loan_id, patron=patron
            )
        except Loan.DoesNotExist:
            return Response({'detail': 'Emprestimo nao encontrado.'}, status=status.HTTP_404_NOT_FOUND)

        if loan.status != Loan.Status.OPEN:
            return Response({'detail': 'Apenas emprestimos em aberto podem ser renovados.'}, status=status.HTTP_400_BAD_REQUEST)

        has_pending = loan.item_copy.bibliographic_record.reservations.filter(
            status__in=[Reservation.Status.QUEUED, Reservation.Status.AVAILABLE]
        ).exclude(patron=patron).exists()
        if has_pending:
            return Response({'detail': 'Renovacao bloqueada: ha reserva pendente de outro leitor.'}, status=status.HTTP_400_BAD_REQUEST)

        from datetime import timedelta
        loan.due_at = loan.due_at + timedelta(days=7)
        loan.save(update_fields=['due_at', 'updated_at'])
        return Response(PatronPortalLoanSerializer(loan).data)
