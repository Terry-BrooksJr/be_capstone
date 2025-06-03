import hashlib
import os
from typing import Union

from django.core.cache import cache
from django.db.models.signals import post_delete, post_save
from django.dispatch import receiver
from django.http.response import JsonResponse
from django.template.response import TemplateResponse
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page, never_cache
from django.views.generic import TemplateView
from loguru import logger
from prometheus_client import Counter
from rest_framework import status
from rest_framework.authtoken.models import Token
from rest_framework.response import Response

VIEW_CACHE_TTL = int(os.environ["VIEW_CACHE_TTL"])


class Metrics:
    """Manages metrics tracking for the api.

    This class provides a comprehensive metrics tracking system for monitoring various application events and performance indicators.
    It uses Prometheus-style counters and histograms to record submission attempts, cache interactions metrics.

    Attributes:
        NAMESPACE (str): The base namespace for all metrics in the web application.
    """

    NAMESPACE = "dozens"
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(Metrics, cls).__new__(cls)
        return cls._instance

    def __init__(self):
        if hasattr(self, "initialized"):
            return
        self.cached_queryset_hit = Counter(
            "cached_queryset_hit",
            "Number of requests served by a cached Queryset",
            ["model"],
        )
        self.cached_queryset_miss = Counter(
            "cached_queryset_miss",
            "Number of  requests not served by a cached Queryset",
            ["model"],
        )
        self.cached_queryset_evicted = Counter(
            "cached_queryset_evicted", "Number of cached Querysets evicted", ["model"]
        )
        self.initialized = True

    def increment_cache(self, model: str, cache_event_type: str) -> None:
        """Tracks cache performance metrics for different database models.

        This method increments the appropriate counter based on the cache interaction type,
        providing insights into cache hit, miss, and eviction rates for specific models.

        Args:
            model(str): String representation of the name the database model being cached.

            cache_event_type(str: The type of cache interaction ('hit', 'miss', or 'eviction').

        Returns:
            None
        """
        if cache_event_type == "hit":
            self.cached_queryset_hit.labels(model=model).inc()
        elif cache_event_type == "miss":
            self.cached_queryset_miss.labels(model=model).inc()
        elif cache_event_type == "eviction":
            self.cached_queryset_evicted.labels(model=model).inc()


# Create a singleton instance for global use
metrics = Metrics()


class CachedTemplateView(TemplateView):
    """A TemplateView that caches its rendered output.

    This class method wraps the standard Django TemplateView with caching, improving performance for repeated requests.
    """

    @classmethod
    def as_view(cls, **initkwargs):  # @NoSelf
        return cache_page(VIEW_CACHE_TTL)(
            super(CachedTemplateView, cls).as_view(**initkwargs)
        )


class NeverCacheMixin(object):
    @method_decorator(never_cache)
    def dispatch(self, *args, **kwargs):
        return super(NeverCacheMixin, self).dispatch(*args, **kwargs)


class CachedResponseMixin:
    """Mixin class to provide caching functionality for API responses.

    This mixin allows views to cache their responses based on user identity and query parameters,
    improving performance by reducing the need for repeated database queries.
    """

    def get_cache_key(self) -> str:
        """Generate a unique cache key based on the request and model information.

        This method constructs a cache key that incorporates the user ID, query parameters,
        and model names associated with the view.

        Returns:
            str: A unique cache key for the current request.

        Raises:
            AttributeError: If the view does not have a 'primary_model' attribute.
        """
        if api_request_key := self.request.META.get("HTTP_AUTHORIZATION"):
            api_key = api_request_key.split(" ")[1]
            user_id = Token.objects.get(key=api_key).user.id
        else:
            user_id = "anonymous"
        query_params = self.request.META["PATH_INFO"]
        query_params_hash = hashlib.md5(
            query_params.encode("utf-8"), usedforsecurity=False
        ).hexdigest()

        # Get the mo
        # del name(s) associated with the view
        model_names = []

        # Add the primary model name
        primary_model = getattr(self, "primary_model", None)
        if primary_model:
            model_names.append(primary_model.__name__)
        else:
            raise AttributeError("View must have a 'primary_model' attribute.")

        # Add the cache_models names
        cache_models = getattr(self, "cache_models", [])
        model_names.extend(model.__name__ for model in cache_models)
        # Combine the model names into a string
        model_names_str = "_".join(model_names)

        return f"{primary_model.__name__}:{self.__class__.__name__}_{model_names_str}_{user_id}_{query_params_hash}_cache_key"

    def get_cached_response(self, cache_key) -> Union[Response | None]:
        """Retrieve cached data using the provided cache key.

        This method checks if there is cached data for the given cache key and returns it if available.

        Args:
            cache_key (str): The cache key to look up.

        Returns:
            Response or None: The cached response if found, otherwise None.
        """
        cached_data = cache.get(cache_key)
        if cached_data is not None:
            logger.debug(
                f"Cache Hit for {self.primary_model.__name__} - Cache Key: {cache_key}"
            )
            metrics.increment_cache(
                model=self.primary_model.__name__, cache_event_type="hit"
            )
            return Response(cached_data, status=status.HTTP_200_OK)
        else:
            logger.debug(
                f"Cache Miss for {self.primary_model.__name__}  - Cache Key: {cache_key}"
            )
            metrics.increment_cache(
                model=self.primary_model.__name__, cache_event_type="miss"
            )
            return None

    def cache_response(self, cache_key, data):
        """Store data in the cache with the specified cache key.

        This method saves the provided data in the cache for a duration of one hour.

        Args:
            cache_key (str): The cache key under which to store the data.
            data: The data to be cached.
        """
        if type(data) in [JsonResponse, TemplateResponse]:
            data = data.render()
        logger.debug(f"New Cache Set {cache_key}: {data}")
        cache.set(cache_key, data, timeout=VIEW_CACHE_TTL)

    def list(self, request, *args, **kwargs) -> Response:
        """Handle GET requests for listing resources with caching.

        This method attempts to return a cached response if available;
        otherwise, it retrieves the data, caches it, and returns the response.

        Args:
            request: The HTTP request object.
            *args: Additional positional arguments.
            **kwargs: Additional keyword arguments.

        Returns:
            Response: The cached or newly generated response.
        """
        cache_key = self.get_cache_key()
        if cached_response := self.get_cached_response(cache_key):
            return cached_response

        # If cache miss, proceed as usual
        queryset = self.filter_queryset(self.get_queryset())

        # Apply pagination if needed
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            data = serializer.data
            self.cache_response(cache_key, data)
            return self.get_paginated_response(data)

        serializer = self.get_serializer(queryset, many=True)
        data = serializer.data
        self.cache_response(cache_key, data)
        return Response(data)

    def retrieve(self, request, *args, **kwargs) -> Response:
        """Handle GET requests for retrieving a single resource with caching.

        This method checks for a cached response and returns it if available;
        otherwise, it retrieves the resource, caches it, and returns the response.

        Args:
            request: The HTTP request object.
            *args: Additional positional arguments.
            **kwargs: Additional keyword arguments.

        Returns:
            Response: The cached or newly generated response.
        """
        cache_key = self.get_cache_key()
        if cached_response := self.get_cached_response(cache_key):
            return cached_response

        # If cache miss, proceed as usual
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        data = serializer.data
        self.cache_response(cache_key, data)
        return Response(data)


@receiver([post_save, post_delete])
def invalidate_cache(sender, **kwargs):
    model_name = sender.__name__
    logger.debug(f"Signal Received For {model_name}")
    # Pattern to match cache keys that include the model name as namespace
    cache_key_pattern = f"{model_name}:*"
    logger.debug(f'Searching For Cache Key Pattern" {cache_key_pattern}')
    if cache_keys := cache.keys(cache_key_pattern):
        cache.delete_many(cache_keys)
        metrics.increment_cache(model=model_name, cache_event_type="eviction")
        logger.info(f"Cache invalidated for model: {model_name}")
    else:
        logger.debug(
            f"No cache keys found for model: {model_name} using {cache_key_pattern}"
        )
