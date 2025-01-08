from rest_framework import permissions


class IsTaskOwnerOrAdmin(permissions.BasePermission):

    def has_object_permission(self, request, view, obj):
        if request.user.is_staff:
            return True
        
        if request.method in permissions.SAFE_METHODS:
            return True
        
        if request.user == obj.user:
            if request.method in ['PUT', 'PATCH'] and 'status' in request.data:
                if 'status' in request.data:
                    return True
                return False
            
        return False
