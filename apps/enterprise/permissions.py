from django.contrib.auth import get_user_model
from rest_framework import permissions

from apps.enterprise.models import Enterprise

User = get_user_model()


class EnterprisePermissions(permissions.BasePermission):
    """
    Permission check for users <> enterprise
    """

    def has_permission(self, request, view):
        enterprise_id = view.kwargs.get('enterprise_id')
        user_id = request.user
        user = User.objects.get(user_id=user_id)
        enterprise = Enterprise.objects.filter(user__in=[user], pk=enterprise_id).all()
        if not enterprise:
            return False
        return True
