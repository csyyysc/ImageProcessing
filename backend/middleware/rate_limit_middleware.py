"""
Rate limiting middleware for FastAPI
"""
import logging
from typing import Optional
from fastapi import Request, status, FastAPI
from fastapi.responses import JSONResponse
from backend.services.rate_limit_service import rate_limit_service

logger = logging.getLogger(__name__)


class RateLimitMiddleware:
    """Middleware to enforce rate limits on API endpoints"""

    def __init__(self, app: FastAPI):
        self.app = app

    async def __call__(self, scope, receive, send):
        if scope["type"] == "http":
            request = Request(scope, receive)

            # Skip rate limiting for health checks and static files
            if self._should_skip_rate_limit(request):
                await self.app(scope, receive, send)
                return

            # Extract user ID from request (you may need to adjust this based on your auth)
            user_id = self._extract_user_id(request)

            if user_id:
                # Check rate limit
                allowed, info = rate_limit_service.check_api_rate_limit(
                    user_id)

                if not allowed:
                    logger.warning(f"Rate limit exceeded for user {user_id}")
                    response = JSONResponse(
                        status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                        content={
                            "detail": "Rate limit exceeded",
                            "error": "RATE_LIMIT_EXCEEDED",
                            "message": info.get("message", "Too many requests"),
                            "retry_after": info.get("reset_time"),
                            "limit": info.get("limit"),
                            "window": info.get("window")
                        }
                    )
                    await response(scope, receive, send)
                    return

                # Add rate limit headers to response
                async def send_wrapper(message):
                    if message["type"] == "http.response.start":
                        headers = dict(message.get("headers", []))
                        headers[b"x-ratelimit-limit"] = str(
                            info.get("limit", 60)).encode()
                        headers[b"x-ratelimit-remaining"] = str(
                            info.get("remaining", 0)).encode()
                        headers[b"x-ratelimit-reset"] = info.get(
                            "reset_time", "").encode()
                        message["headers"] = list(headers.items())
                    await send(message)

                await self.app(scope, receive, send_wrapper)
            else:
                # No user ID, proceed without rate limiting
                await self.app(scope, receive, send)
        else:
            await self.app(scope, receive, send)

    def _should_skip_rate_limit(self, request: Request) -> bool:
        """Check if request should skip rate limiting"""

        path = request.url.path
        method = request.method

        # Skip rate limiting for these paths
        skip_paths = [
            "/health",
            "/docs",
            "/openapi.json",
            "/redoc",
            "/favicon.ico"
        ]

        # Skip rate limiting for read-only statistics endpoints
        read_only_paths = [
            "/api/images/download/stats",  # Download statistics
            "/api/images/total",           # Total image count
            "/api/images",                 # Image listing (GET requests only)
        ]

        # Skip rate limiting for GET requests to read-only paths
        if method == "GET" and any(path.startswith(skip_path) for skip_path in read_only_paths):
            return True

        return any(path.startswith(skip_path) for skip_path in skip_paths)

    def _extract_user_id(self, request: Request) -> Optional[int]:
        """Extract user ID from request"""

        try:
            # Try to get user ID from JWT token in Authorization header
            auth_header = request.headers.get("authorization")
            if auth_header and auth_header.startswith("Bearer "):
                token = auth_header.split(" ")[1]
                from backend.services.auth_service import auth_service
                user_id = auth_service.get_user_from_token(token)
                if user_id:
                    return user_id.get('id')

            # Try to get user_id from query parameters (for backward compatibility)
            user_id = request.query_params.get("user_id")
            if user_id:
                return int(user_id)

        except Exception as e:
            logger.debug(f"Could not extract user ID: {e}")

        return None


def add_rate_limit_middleware(app: FastAPI):
    """Add rate limiting middleware to FastAPI app"""

    app.add_middleware(RateLimitMiddleware)
    logger.info("Rate limiting middleware added")
