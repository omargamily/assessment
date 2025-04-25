from rest_framework.permissions import BasePermission


class IsMerchantGroup(BasePermission):
    message = 'User must be in the Merchant group.'

    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        return request.user.groups.filter(name='Merchant').exists()


class IsUserGroup(BasePermission):
    message = 'User must be in the User group.'

    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        return request.user.groups.filter(name='User').exists()


class IsStaffGroup(BasePermission):
    message = 'User must be in the Staff group.'

    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        return request.user.groups.filter(name='Staff').exists()