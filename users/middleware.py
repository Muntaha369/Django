import logging
import time

logger = logging.getLogger("users.request")


class RequestLoggingMiddleware:
    """
    Middleware wraps the whole request/response cycle.

    Django builds a chain of middleware. Each one receives the request, may do
    work, calls the next layer (eventually the view), then may do work again on
    the way out:

        Request -> middleware -> view -> response -> middleware -> Client

    This example logs when a request enters and leaves, plus how long it took.
    (It does NOT implement authentication -- use DRF permission classes for
    that. Middleware is best for cross-cutting concerns like logging, timing,
    request IDs, CORS headers, etc.)
    """

    def __init__(self, get_response):
        # Called once at startup. `get_response` is the *next* layer in the
        # chain: call it to continue the request, or skip it to short-circuit.
        self.get_response = get_response

    def __call__(self, request):
        started_at = time.perf_counter()

        # Everything before get_response() runs on the way IN.
        logger.info("--> %s %s", request.method, request.path)

        # This line runs the rest of the chain, ending with the view.
        response = self.get_response(request)

        # Everything after it runs on the way OUT (the view has already
        # produced a response at this point).
        elapsed_ms = (time.perf_counter() - started_at) * 1000
        logger.info(
            "<-- %s %s -> %s (%.1f ms)",
            request.method,
            request.path,
            response.status_code,
            elapsed_ms,
        )
        return response
