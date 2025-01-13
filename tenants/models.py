from django.db import models

class Tenant(models.Model):
    domain = models.CharField(max_length=255, unique=True)
    name = models.CharField(max_length=255)

    def __str__(self):
        return f'{self.name} {self.domain}'

    class Meta:
        permissions = [
            ('can_access_tenant', 'Can access tenant'),
        ]

class Organization(models.Model):
    tenant = models.ForeignKey(Tenant, on_delete=models.CASCADE, related_name="organizations")
    name = models.CharField(max_length=255)

    def __str__(self):
        return f"{self.name} ({self.tenant.name})"

    class Meta:
        permissions = [
            ('can_access_organization', 'Can access organization'),
        ]

class Department(models.Model):
    organization = models.ForeignKey(Organization, on_delete=models.CASCADE, related_name="departments")
    name = models.CharField(max_length=255)

    def __str__(self):
        return f"{self.name} ({self.organization.name})"

    class Meta:
        permissions = [
            ('can_access_department', 'Can access department'),
        ]

class Customer(models.Model):
    department = models.ForeignKey(Department, on_delete=models.CASCADE, related_name="customers")
    first_name = models.CharField(max_length=255)
    last_name = models.CharField(max_length=255)
    email = models.EmailField()

    def __str__(self):
        return f"{self.first_name} {self.last_name} ({self.department.name})"
    class Meta:
        permissions = [
            ('can_access_customer', 'Can access customer'),
        ]
