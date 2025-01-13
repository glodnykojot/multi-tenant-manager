from django.shortcuts import get_object_or_404
from rest_framework import viewsets
from rest_framework.authentication import TokenAuthentication
from rest_framework.exceptions import ValidationError, PermissionDenied
from rest_framework.response import Response
from rest_framework import status
from .models import Tenant, Organization, Department, Customer
from .serializers import TenantSerializer, OrganizationSerializer, DepartmentSerializer, CustomerSerializer
from .permissions import TenantPermission, OrganizationPermission, DepartmentPermission, CustomerPermission
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

class TenantViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing tenants.
    """
    queryset = Tenant.objects.all()
    serializer_class = TenantSerializer
    permission_classes = [TenantPermission]
    authentication_classes = [TokenAuthentication]

class OrganizationViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing organizations.
    Organizations are filtered based on the current tenant.
    """
    queryset = Organization.objects.all()
    serializer_class = OrganizationSerializer
    permission_classes = [OrganizationPermission]

    def get_queryset(self):
        """
        Retrieve organizations associated with the active tenant.
        """
        tenant = self.request.tenant
        return Organization.objects.filter(tenant=tenant)

    def perform_create(self, serializer):
        """
        Automatically associate the organization with the active tenant during creation.
        """
        tenant = self.request.tenant
        serializer.save(tenant=tenant)

    def validate_organization(self, instance):
        """
        Ensure the organization belongs to the current tenant.
        """
        if instance.tenant != self.request.tenant:
            raise PermissionDenied("You do not have permission to modify this organization.")

    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        self.validate_organization(instance)
        return super().update(request, *args, **kwargs)

    def partial_update(self, request, *args, **kwargs):
        instance = self.get_object()
        self.validate_organization(instance)
        return super().partial_update(request, *args, **kwargs)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        self.validate_organization(instance)
        return super().destroy(request, *args, **kwargs)

class DepartmentViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing departments.
    Departments are filtered by the organization and tenant.
    """
    queryset = Department.objects.all()
    serializer_class = DepartmentSerializer
    permission_classes = [DepartmentPermission]
    authentication_classes = [TokenAuthentication]

    @swagger_auto_schema(
        manual_parameters=[
            openapi.Parameter('organization', openapi.IN_QUERY, description="ID of the organization", type=openapi.TYPE_INTEGER)
        ]
    )
    def list(self, request, *args, **kwargs):
        """
        List all departments within a specified organization.
        """
        return super().list(request, *args, **kwargs)

    def get_queryset(self):
        """
        Retrieve departments filtered by organization and tenant.
        """
        if 'pk' in self.kwargs:
            return Department.objects.filter(
                pk=self.kwargs['pk'],
                organization__tenant=self.request.tenant
            )

        organization_id = self.request.query_params.get('organization')
        if not organization_id:
            raise ValidationError({"detail": "Parameter 'organization' is required in query params."})

        if not Organization.objects.filter(
            id=organization_id, tenant=self.request.tenant
        ).exists():
            raise ValidationError({"detail": "Invalid organization for the current tenant."})

        return Department.objects.filter(
            organization=organization_id,
            organization__tenant=self.request.tenant
        ).select_related('organization', 'organization__tenant')

    def perform_create(self, serializer):
        """
        Create a new department linked to a specific organization and tenant.
        """
        organization_id = self.request.data.get('organization')
        if not organization_id:
            raise ValueError("Organization is required in the request body.")

        try:
            organization = Organization.objects.get(
                id=organization_id,
                tenant=self.request.tenant
            )
        except Organization.DoesNotExist:
            raise ValidationError({"detail": "Invalid organization for the current tenant."})

        serializer.save(organization=organization)

    def validate_department(self, instance, organization_id=None):
        """
        Ensure the department belongs to the current tenant and organization.
        """
        if instance.organization.tenant != self.request.tenant:
            raise PermissionDenied("You do not have permission to modify this department.")

        if organization_id:
            organization = get_object_or_404(Organization, id=organization_id, tenant=self.request.tenant)
            if instance.organization != organization:
                raise PermissionDenied("You cannot move the department to a different organization.")

    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        organization_id = request.data.get('organization')
        self.validate_department(instance, organization_id)
        return super().update(request, *args, **kwargs)

    def partial_update(self, request, *args, **kwargs):
        instance = self.get_object()
        organization_id = request.data.get('organization')
        self.validate_department(instance, organization_id)
        return super().partial_update(request, *args, **kwargs)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        self.validate_department(instance)
        return super().destroy(request, *args, **kwargs)

class CustomerViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing customers.
    Customers are filtered by department and tenant.
    """
    queryset = Customer.objects.all()
    serializer_class = CustomerSerializer
    permission_classes = [CustomerPermission]
    authentication_classes = [TokenAuthentication]

    @swagger_auto_schema(
        manual_parameters=[
            openapi.Parameter('department', openapi.IN_QUERY, description="ID of the department", type=openapi.TYPE_INTEGER)
        ]
    )
    def list(self, request, *args, **kwargs):
        """
        List customers within a specific department.
        """
        queryset = self.get_queryset()
        if not queryset.exists():
            return Response(
                {"detail": "No customers found for the given department."},
                status=status.HTTP_404_NOT_FOUND
            )
        return super().list(request, *args, **kwargs)

    def get_queryset(self):
        """
        Retrieve customers filtered by department and tenant.
        """
        if 'pk' in self.kwargs:
            return Customer.objects.filter(
                pk=self.kwargs['pk'],
                department__organization__tenant=self.request.tenant,
            )

        department_id = self.request.query_params.get('department')
        if not department_id:
            raise ValidationError({"detail": "Parameter 'department' is required in query params."})

        if not Department.objects.filter(
            id=department_id, organization__tenant=self.request.tenant
        ).exists():
            raise ValidationError({"detail": "Invalid department for the current tenant."})

        return Customer.objects.filter(
            department=department_id,
            department__organization__tenant=self.request.tenant
        ).select_related('department__organization')

    def perform_create(self, serializer):
        """
        Automatically associate the customer with a department and its hierarchy.
        """
        department_id = self.request.data.get('department')
        department = Department.objects.get(
            id=department_id,
            organization__tenant=self.request.tenant
        )
        serializer.save(department=department)

    def validate_customer(self, instance, department_id=None):
        """
        Ensure the customer belongs to the current tenant and department.
        """
        if instance.department.organization.tenant != self.request.tenant:
            raise PermissionDenied("You do not have permission to modify this customer.")

        if department_id:
            department = get_object_or_404(Department, id=department_id, organization__tenant=self.request.tenant)
            if instance.department != department:
                raise PermissionDenied("You cannot move the customer to a different department.")

    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        department_id = request.data.get('department')
        self.validate_customer(instance, department_id)
        return super().update(request, *args, **kwargs)

    def partial_update(self, request, *args, **kwargs):
        instance = self.get_object()
        department_id = request.data.get('department')
        self.validate_customer(instance, department_id)
        return super().partial_update(request, *args, **kwargs)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        self.validate_customer(instance)
        return super().destroy(request, *args, **kwargs)
