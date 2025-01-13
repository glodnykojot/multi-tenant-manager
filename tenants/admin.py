from django.contrib import admin
from .models import  Tenant, Department, Organization, Customer

admin.site.register(Tenant)
admin.site.register(Department)
admin.site.register(Organization)
admin.site.register(Customer)
