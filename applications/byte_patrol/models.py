from django.core.exceptions import ValidationError
from django.core.validators import validate_ipv46_address
from django.db import models


class IPAllowList(models.Model):
    """Represents an IP address or CIDR block that is allowed access to protected resources.

    This model stores individual IP addresses or CIDR notations, along with optional descriptions and activation status.
    """

    ip_address = models.CharField(
        max_length=50,
        unique=True,
        validators=[validate_ipv46_address],
        help_text="IP address in IPv4 or IPv6 format",
    )
    description = models.CharField(
        max_length=255, blank=True, help_text="Optional description for this IP address"
    )
    is_active = models.BooleanField(
        default=True,
        help_text="If unchecked, this IP will not be allowed even if in the list",
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "IP Allow List Entry"
        verbose_name_plural = "IP Allow List Entries"
        ordering = ["ip_address"]
        db_table = "ip_allow_list"

    def __str__(self):
        return f"{self.ip_address} - {self.description or 'No description'}"

    def clean(self):
        try:
            validate_ipv46_address(self.ip_address)
        except ValidationError:
            if "/" not in self.ip_address:
                raise
            try:
                import ipaddress

                ipaddress.ip_network(self.ip_address, strict=False)
            except (ValueError, ImportError) as e:
                raise ValidationError(
                    {
                        "ip_address": "Enter a valid IPv4 or IPv6 address or CIDR notation."
                    }
                ) from e


class ProtectedPath(models.Model):
    """Represents a URL pattern that is protected by IP restrictions.

    This model defines URL patterns that require IP allow list checks, with optional descriptions and activation status.
    """

    path_pattern = models.CharField(
        max_length=255, help_text="URL pattern to restrict (can use regex patterns)"
    )
    description = models.CharField(
        max_length=255, blank=True, help_text="Description of what this path protects"
    )
    is_active = models.BooleanField(
        default=True, help_text="If unchecked, this path will not be IP restricted"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Protected Path"
        verbose_name_plural = "Protected Paths"
        ordering = ["path_pattern"]
        db_table = "protected_routes"

    def __str__(self):
        return f"{self.path_pattern} - {self.description or 'No description'}"
