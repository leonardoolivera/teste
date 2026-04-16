from rest_framework.permissions import SAFE_METHODS, BasePermission

from apps.users.models import User


OPERATOR_ROLES = {
    User.Role.ADMIN,
    User.Role.MANAGER,
    User.Role.LIBRARIAN,
    User.Role.ASSISTANT,
    User.Role.INTEGRATION,
}

MANAGEMENT_ROLES = {
    User.Role.ADMIN,
    User.Role.MANAGER,
}


class IsOperator(BasePermission):
    message = 'Operator authentication is required.'

    def has_permission(self, request, view):
        user = request.user
        return bool(
            user
            and user.is_authenticated
            and (user.is_superuser or user.role in OPERATOR_ROLES)
        )


class IsAdminOrManager(BasePermission):
    message = 'Admin or manager access is required.'

    def has_permission(self, request, view):
        user = request.user
        return bool(
            user
            and user.is_authenticated
            and (user.is_superuser or user.role in MANAGEMENT_ROLES)
        )


class IsReadOnlyOrOperator(BasePermission):
    def has_permission(self, request, view):
        if request.method in SAFE_METHODS:
            return True
        return IsOperator().has_permission(request, view)
