# accounts/permissions.py
from rest_framework.permissions import BasePermission, SAFE_METHODS


class IsMerchantRole(BasePermission):
    message = 'User must have the Merchant role.'

    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        return request.user.role == 'merchant'


class IsUserRole(BasePermission):
    message = 'User must have the User role.'

    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        return request.user.role == 'user'


class IsStaffRole(BasePermission):
    message = 'User must have the Staff role.'

    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        return request.user.role == 'staff'


class IsOwnerOrMerchantOfPlan(BasePermission):
    message = 'You do not have permission to access this plan.'

    def has_object_permission(self, request, view, obj):
        if not request.user or not request.user.is_authenticated:
            return False
        return obj.user == request.user or obj.merchant == request.user