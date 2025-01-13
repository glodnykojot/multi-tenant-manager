# MultiTenantManager - Django Multi-Tenant Application

**MultiTenantManager** is a Django-based application for managing multiple tenants within a single application instance. It ensures data isolation across tenants and simplifies access management and CRUD operations in a multi-tenant setup. 

The system follows a clear hierarchical data structure:  
**Tenant → Organization → Department → Customer**

This architecture is ideal for scalable, secure, and modular SaaS platforms or any application requiring tenant-specific data segregation and management.
## Requirements

To run the project, you will need:

- Python 3.x  
- Django  
- Django REST Framework  
- Docker  
- Docker Compose  
- PostgreSQL

## Installation

1. **Clone the repository**:

```bash
git clone git clone git@github.com:multi-tenant-manager.git
cd multi-tenant-manager
```

2. **Build conteiners**
``` bash
docker-compose up --build
```
3. **Run migrations**

```bash
docker-compose exec web python manage.py migrate
```
4. **Create superuser to login into admin panel**
```bash
docker-compose exec web python manage.py createsuperuser
```

## Description 
**Main Features of the Program**
1. **CRUD Operations**
The program enables CRUD operations for resources such as tenants, organizations, departments, and customers. Data is hierarchically filtered based on model relationships.

2. **Tenant Data Isolation**
Tenant data is isolated using middleware that identifies the tenant based on the subdomain and attaches it to API requests.

3. **Automatic Validation and Permissions**
The program ensures that resources belong to the active tenant and enforces user access based on their roles and permissions.

4. **API Documentation**
Endpoints are integrated with Swagger documentation using drf-yasg, facilitating easier API usage.

5. **Error Handling**
Detailed error messages inform users about missing data, improper access, or invalid parameters.

## Middleware for Tenant Filtering
The custom middleware is designed to dynamically identify and manage tenants based on the subdomain in the URL. This approach ensures seamless tenant-specific data access and isolation without requiring explicit tenant identifiers in every request.

1. **Extracting the Subdomain**
   - The middleware intercepts each request and extracts the subdomain (tenant domain) from the URL.
   - Example: In the URL `my_domain.localhost:8000`, the subdomain `my_domain` is identified as the tenant.

2. **Tenant Validation**
   - The middleware verifies the extracted subdomain against the database to check if a tenant with the corresponding domain exists.
   - If a tenant is found, it is attached to the request as `request.tenant`.
   - If no tenant is found or the subdomain is invalid, the middleware returns an error response (`400 Bad Request`) with an appropriate message.

3. **Routing and Data Isolation**
   - All subsequent queries and operations are scoped to the data associated with the identified tenant.
   - This ensures data isolation and prevents unauthorized access to data from other tenants.

4. **Dynamic Modifications**
   - For specific endpoints (e.g., creating an organization), the middleware automatically injects the tenant ID into the request body to ensure tenant-specific association.
   - This simplifies client-side implementation by removing the need to explicitly provide tenant information.
