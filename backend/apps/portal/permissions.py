from rest_framework.permissions import BasePermission


class IsPatron(BasePermission):
    message = 'Autenticacao de leitor necessaria.'

    def has_permission(self, request, view):
        user = request.user
        if not (user and user.is_authenticated):
            return False
        return hasattr(user, 'patron_profile')
