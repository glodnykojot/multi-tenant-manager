import json
from django.http import JsonResponse
from rest_framework.authentication import TokenAuthentication
from rest_framework.exceptions import AuthenticationFailed
from rest_framework import status
from tenants.models import Tenant

PUBLIC_PATHS = ['/api/token/', '/api/doc/', '/admin/']

class TenantMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):

        if not any(request.path.startswith(public_path) for public_path in PUBLIC_PATHS):
            try:
                domain = self._extract_domain(request)
                print(f"Extracted domain: {domain}")

                if request.path.startswith('/api/tenants/'):
                    self._handle_tenant_endpoint(request, domain)
                else:
                    tenant = self._attach_tenant_to_request(request, domain)
                    if request.path.startswith('/api/organizations/'):
                        self._add_tenant_to_body(request, tenant)
            
            except ValueError as e:
                return JsonResponse({"detail": f"{e}"}, status=400)
        return self.get_response(request)

    def _extract_domain(self, request):
        """Extracts the domain from the request host."""
        host = request.get_host().split(':')[0]
        print(host)
        domain = host.split('.')[0].lower()
        return domain

    def _handle_tenant_endpoint(self, request, domain):
        """Handles setting the domain in the request body for tenant creation."""
        if request.method == "POST":
            try:
                data = json.loads(request.body)
                data["domain"] = domain
                request._body = json.dumps(data).encode('utf-8')
            except ValueError as e:
                raise ValueError(f"Erorr during adding tenant to the request body.") from e
            
        
    def _attach_tenant_to_request(self, request, domain):
        """Attaches the tenant object to the request based on the domain."""
        try:
            tenant = Tenant.objects.get(domain=domain)
            print(f"Tenant attached: {tenant}")
            request.tenant = tenant
            return tenant
        except Tenant.DoesNotExist:
            raise ValueError("Tenant not found for this domain.")
            
    def _add_tenant_to_body(self, request, tenant):
        """Adds tenant ID to the request body for specific endpoints."""
        if request.method in ['POST', 'PUT', 'PATCH']:
            try:
                data = json.loads(request.body)
                data["tenant"] = tenant.id
                request._body = json.dumps(data).encode('utf-8')
                print(f"Added tenant_id to request body: {tenant.id}")
            except (ValueError, TypeError) as e:
                raise ValueError(f"Invalid request body: {e}")




class TokenAuthenticationMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if any(request.path.startswith(public_path) for public_path in PUBLIC_PATHS):
            return self.get_response(request)
        # Próba uzyskania tokenu z nagłówka
        token = request.headers.get('Authorization')
        if not token:
            return JsonResponse({'detail': 'Authorization token required.'}, status=401)

        # Usunięcie prefiksu "Bearer" (jeśli jest)
        if token.startswith('token '):
            token = token[6:]  # Usuwamy "Token " z początku (6 znaków
        # Próba autentykacji za pomocą TokenAuthentication
        try:
            user, _ = TokenAuthentication().authenticate_credentials(token)
            request.user = user  # Ustawiamy użytkownika w obiekcie request
        except AuthenticationFailed:
            return JsonResponse({'detail': 'Invalid token.'}, status=401)

        return self.get_response(request)