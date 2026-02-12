from rest_framework import permissions

class IsOwnerOrAdmin(permissions.BasePermission):
    """
    Custom permission: Allow write access only to the owner or admin users.
    """

    def has_object_permission(self, request, view, obj):
        """
        Check if user has permission to modify object.
        """
        # Read permissions are allowed to any request
        if request.method in permissions.SAFE_METHODS:
            return True
        # Write permissions: owner or admin
        if hasattr(obj, 'owner') and obj.owner is not None:
            return obj.owner == request.user or request.user.is_staff
        # If no owner (seed/system), only admin can modify
        return request.user.is_staff
