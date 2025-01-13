from rest_framework import serializers
from .models import Tenant, Organization, Department, Customer


class TenantSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tenant
        fields = ['id', 'name', 'domain']
        read_only_fields = ['id']


class OrganizationSerializer(serializers.ModelSerializer):

    class Meta:
        model = Organization
        fields = ['id', 'name', 'tenant']
        read_only_fields = ['id']
    
    def create(self, validated_data):
        # Pobierz tenant z requestu i przypisz go do organizacji
        tenant = self.context['request'].tenant
        if not tenant:
            raise serializers.ValidationError("No active tenant found.")
        validated_data['tenant'] = tenant
        return super().create(validated_data)

class DepartmentSerializer(serializers.ModelSerializer):
    organization = serializers.PrimaryKeyRelatedField(
        queryset=Organization.objects.all(),
        error_messages={
            'does_not_exist': 'Organization with this ID does not exist.',
            'invalid': 'Invalid tenant ID.',
        }
    )

    class Meta:
        model = Department
        fields = ['id', 'name', 'organization']
        read_only_fields = ['id']


class CustomerSerializer(serializers.ModelSerializer):
    department = serializers.PrimaryKeyRelatedField(
        queryset=Department.objects.all(),
        error_messages={
            'does_not_exist': 'Departament with this ID does not exist.',
            'invalid': 'Invalid tenant ID.',
        }
    )

    class Meta:
        model = Customer
        fields = ['id', 'first_name', 'last_name', 'email', 'department']
        read_only_fields = ['id']