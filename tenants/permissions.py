from rest_framework.permissions import BasePermission
from rest_framework.exceptions import PermissionDenied

from rest_framework.permissions import BasePermission
from rest_framework.exceptions import PermissionDenied


class MultiTenantPermission(BasePermission):
    '''Reusable class to check permissions'''
    permission_required = None  # Np. 'tenants.can_access_tenant'
    related_field = None
    
    def check_permission(self, request):
        """Check global permissions."""
        if request.user.is_authenticated:
            print(self.permission_required)
            print(request.user.get_user_permissions())
            print(request.user.has_perm(self.permission_required))
            if self.permission_required and request.user.has_perm(self.permission_required):
                return True
            raise PermissionDenied("You do not have the required permissions.")
        raise PermissionDenied("You must be authenticated to access this resource.")

    def get_related_field_value(self, obj):
        """
        Get value of `related_field` (for example 'organization.tenant').
        """
        if not self.related_field:
            raise PermissionDenied("related_field is not defined.")
        fields = self.related_field.split('.')
        value = obj
        for field in fields:
            value = getattr(value, field, None)
            if value is None:
                raise PermissionDenied(f"Field '{field}' does not exist on the object.")
        return value

    def has_permission(self, request, view):
        """Check permission."""
        return self.check_permission(request)

    def has_object_permission(self, request, view, obj):
        """
        Check permission for object.
        """
        if not self.check_permission(request):
            return False

        related_value = self.get_related_field_value(obj)
        
        if related_value == request.tenant:
            return True
        
        raise PermissionDenied(f"You do not have permission to access this {self.related_field}.")


class TenantPermission(MultiTenantPermission):
    permission_required = 'tenants.can_access_tenant'
    related_field = None

class OrganizationPermission(MultiTenantPermission):
    permission_required = 'tenants.can_access_organization'
    related_field = 'tenant'

class DepartmentPermission(MultiTenantPermission):
    permission_required = 'tenants.can_access_department'
    related_field = 'organization.tenant'

class CustomerPermission(MultiTenantPermission):
    permission_required = 'tenants.can_access_customer'
    related_field = 'department.organization.tenant'
