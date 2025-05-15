import re
import ipaddress
from loguru import logger
from django.conf import settings
from django.core.cache import cache
from django.http import HttpResponseForbidden
from django.utils.deprecation import MiddlewareMixin
from operator import attrgetter


class IPRestrictionMiddleware(MiddlewareMixin):
    """Middleware that restricts access to protected paths based on client IP address.

    This middleware checks incoming requests against an allow list of IP addresses and protected URL patterns, denying access if the client's IP is not permitted.
    """

    CACHE_KEY_ALLOWED_IPS = 'ip_restriction_allowed_ips'
    CACHE_KEY_PROTECTED_PATHS = 'ip_restriction_protected_paths'
    CACHE_TIMEOUT = getattr(settings, 'BYTE_PATROL_CACHE_TIMEOUT', 300)  # 5 minutes default
    
    def __init__(self, get_response=None):
        self.get_response = get_response
        super().__init__(get_response)
        
    def _get_client_ip(self, request):
        """
        Get the client's IP address from request headers or REMOTE_ADDR.
        Handles cases where the request might be behind a proxy.
        """
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        return (
            x_forwarded_for.split(',')[0].strip()
            if x_forwarded_for
            else request.META.get('REMOTE_ADDR')
        )
    
    def _is_path_restricted(self, path):
        """
        Check if the current path matches any protected path patterns.
        """
        # Get protected paths from cache or DB
        protected_paths = self._get_protected_paths()

        return any(re.match(pattern, path) for pattern in protected_paths)
    
    def _is_ip_allowed(self, ip):
        """
        Check if the given IP is in the allowed list.
        """
        # Get allowed IPs from cache or combined sources
        allowed_ips = self._get_allowed_ips()
        
        # Direct match check
        if ip in allowed_ips:
            return True
        
        # CIDR network check
        try:
            client_ip = ipaddress.ip_address(ip)
            for allowed_ip in allowed_ips:
                if '/' in allowed_ip:  # This is a network range
                    try:
                        network = ipaddress.ip_network(allowed_ip, strict=False)
                        if client_ip in network:
                            return True
                    except ValueError:
                        logger.warning(f"Invalid network format: {allowed_ip}")
        except ValueError:
            logger.warning(f"Invalid IP format: {ip}")
        
        return False

    def _get_allowed_ips(self):
        """
        Get allowed IPs from cache or build from settings and database.
        """
        allowed_ips = cache.get(self.CACHE_KEY_ALLOWED_IPS)
        
        if allowed_ips is None:
            # Get IPs from settings
            settings_ips = getattr(settings, 'BYTE_PATROL_ALLOWED_IPS', [])
            
            # Get IPs from database
            try:
                from .models import IPAllowList
                db_ips = list(IPAllowList.objects.filter(
                    is_active=True
                ).values_list('ip_address', flat=True))
            except ImportError:
                db_ips = []
                logger.warning("Could not import IPAllowList model")
            
            # Combine and deduplicate
            allowed_ips = list(set(settings_ips + db_ips))
            
            # Cache the result
            cache.set(self.CACHE_KEY_ALLOWED_IPS, allowed_ips, self.CACHE_TIMEOUT)
            
        return allowed_ips

    def _get_protected_paths(self):
        """
        Get protected path patterns from cache or build from settings and database.
        """
        protected_paths = cache.get(self.CACHE_KEY_PROTECTED_PATHS)
        
        if protected_paths is None:
            # Get paths from settings
            settings_paths = getattr(settings, 'BYTE_PATROL_PROTECTED_PATHS', [])
            
            # Get paths from database
            try:
                from .models import ProtectedPath
                db_paths = list(ProtectedPath.objects.filter(
                    is_active=True
                ).values_list('path_pattern', flat=True))
            except ImportError:
                db_paths = []
                logger.warning("Could not import ProtectedPath model")
            
            # Combine and deduplicate
            protected_paths = list(set(settings_paths + db_paths))
            
            # Cache the result
            cache.set(self.CACHE_KEY_PROTECTED_PATHS, protected_paths, self.CACHE_TIMEOUT)
            
        return protected_paths

    def process_request(self, request):
        """
        Process each request to check if IP restriction should be applied.
        """
        # Skip IP check for paths that aren't restricted
        if not self._is_path_restricted(request.path):
            return None

        # Get client IP
        client_ip = self._get_client_ip(request)

        # Check if IP is allowed
        if not self._is_ip_allowed(client_ip):
            logger.warning(f"Access denied for IP {client_ip} to {request.path}")

            return getattr(
                settings,
                'BYTE_PATROLFORBIDDEN_RESPONSE',
                HttpResponseForbidden(
                    "Access Denied: Your IP address is not allowed."
                ),
            )
        return None

    def invalidate_cache(self):
        """
        Invalidate the IP and path caches.
        """
        cache.delete(self.CACHE_KEY_ALLOWED_IPS)
        cache.delete(self.CACHE_KEY_PROTECTED_PATHS)
