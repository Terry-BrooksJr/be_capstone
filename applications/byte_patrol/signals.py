from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from .models import IPAllowList, ProtectedPath
from .middleware import IPRestrictionMiddleware

@receiver([post_save, post_delete], sender=IPAllowList)
@receiver([post_save, post_delete], sender=ProtectedPath)
def invalidate_ip_restriction_cache(sender, **kwargs):
    """
    Invalidate the cache when IP allow list or protected paths are modified.
    """
    IPRestrictionMiddleware().invalidate_cache()
