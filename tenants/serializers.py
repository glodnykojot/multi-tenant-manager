from rest_framework import serializers
from .models import Tenant, Organization, Department, Customer


class TenantSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tenant
        fields = ['tenant_id', 'name', 'domain']
        read_only_fields = ['tenant_id']


class OrganizationSerializer(serializers.ModelSerializer):
    tenant = TenantSerializer()

    class Meta:
        model = Organization
        fields = ['id', 'name', 'tenant']
        read_only_fields = ['id']


class DepartmentSerializer(serializers.ModelSerializer):
    organization = OrganizationSerializer()

    class Meta:
        model = Department
        fields = ['id', 'name', 'organization']
        read_only_fields = ['id']


class CustomerSerializer(serializers.ModelSerializer):
    department = DepartmentSerializer()

    class Meta:
        model = Customer
        fields = ['id', 'first_name', 'last_name', 'email', 'department']
        read_only_fields = ['id']