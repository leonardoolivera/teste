from django.contrib.auth import authenticate, logout
from rest_framework import status, viewsets
from rest_framework.authtoken.models import Token
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.core.permissions import IsAdminOrManager, IsOperator
from .models import Patron, PatronBlock, User
from .serializers import AuthLoginSerializer, PatronBlockSerializer, PatronSerializer, UserSerializer


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.select_related('library_branch').all()
    serializer_class = UserSerializer
    permission_classes = [IsAdminOrManager]
    filterset_fields = ['role', 'library_branch', 'is_active']
    search_fields = ['email', 'first_name', 'last_name']
    ordering = ['email']


class PatronViewSet(viewsets.ModelViewSet):
    queryset = Patron.objects.select_related('user', 'library_branch').all()
    serializer_class = PatronSerializer
    permission_classes = [IsOperator]
    filterset_fields = ['category', 'status', 'library_branch']
    search_fields = ['full_name', 'registration_code', 'email']
    ordering = ['full_name']


class PatronBlockViewSet(viewsets.ModelViewSet):
    queryset = PatronBlock.objects.select_related('patron').all()
    serializer_class = PatronBlockSerializer
    permission_classes = [IsOperator]
    filterset_fields = ['is_active', 'patron']
    search_fields = ['patron__full_name', 'reason']
    ordering = ['-created_at']


class AuthLoginApi(APIView):
    authentication_classes = []
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = AuthLoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = authenticate(request, email=serializer.validated_data['email'], password=serializer.validated_data['password'])
        if user is None:
            return Response({'detail': 'Invalid credentials.'}, status=status.HTTP_400_BAD_REQUEST)

        token, _ = Token.objects.get_or_create(user=user)
        return Response({'token': token.key, 'user': UserSerializer(user).data})


class AuthMeApi(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        return Response(UserSerializer(request.user).data)


class AuthLogoutApi(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        Token.objects.filter(user=request.user).delete()
        logout(request)
        return Response(status=status.HTTP_204_NO_CONTENT)
