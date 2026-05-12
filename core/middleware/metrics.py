# core/middleware/metrics.py
"""Middleware for request timing metrics and response time tracking."""

import logging
import time

from django.utils.deprecation import MiddlewareMixin

logger = logging.getLogger(__name__)


class RequestMetricsMiddleware(MiddlewareMixin):
    """Middleware that measures request duration and adds response time headers.

    This middleware records the start time of each request, calculates the
    processing duration, logs the request metrics, and adds a
    X-Response-Time header to the response.
    """

    def process_request(self, request):
        """Record the request start time before processing.

        Args:
            request: The HTTP request object.
        """
        request.start_time = time.time()

    def process_response(self, request, response):
        """Calculate request duration and log metrics after processing.

        Args:
            request: The HTTP request object.
            response: The HTTP response object.

        Returns:
            The HTTP response object with added X-Response-Time header.
        """
        if hasattr(request, 'start_time'):
            duration = time.time() - request.start_time
            logger.info(f"{request.method} {request.path} - {duration:.3f}s - {response.status_code}")

            # Add response time header for client-side metrics
            response['X-Response-Time'] = f"{duration:.3f}s"
        return response