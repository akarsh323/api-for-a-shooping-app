from rest_framework import permissions

class IsManagerOrReadOnly(permissions.BasePermission):
   

    def has_permission(self, request, view):
        # Allow GET, HEAD or OPTIONS requests.
        if request.method in permissions.SAFE_METHODS:
            return True
        # Check if the user is in the 'manager' group.
        return request.user.groups.filter(name='Manager').exists()
    def has_object_permission(self, request, view, obj):
        # Allow GET, HEAD or OPTIONS requests.
        if request.method in permissions.SAFE_METHODS:
            return True
        # Check if the user is in the 'manager' group.
        return request.user.groups.filter(name='Manager').exists()


from rest_framework.permissions import BasePermission

class IsManager(BasePermission):
    
    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False
        
        return request.user.groups.filter(name='Manager').exists()
