"""
Rate limiting service for API calls and downloads
"""
import logging
import threading
from typing import Dict, Tuple
from datetime import datetime, timezone, timedelta
from collections import defaultdict, deque

logger = logging.getLogger(__name__)


class RateLimitService:
    """Service for managing rate limits and download quotas"""

    def __init__(self):
        # API rate limiting: 60 calls per 60 seconds
        self.api_calls = defaultdict(deque)  # user_id -> deque of timestamps
        self.api_limit = 60  # calls
        self.api_window = 60  # seconds

        # Download limiting: 500 downloads per day
        self.daily_downloads = defaultdict(int)  # user_id -> count
        self.download_limit = 500  # downloads per day
        self.last_reset_date = datetime.now(timezone.utc).date()

        # Thread lock for thread safety
        self.lock = threading.Lock()

    def _cleanup_old_calls(self, user_id: int, now: datetime):
        """Remove API calls older than the window"""

        cutoff_time = now - timedelta(seconds=self.api_window)
        user_calls = self.api_calls[user_id]

        # Remove calls older than the window
        while user_calls and user_calls[0] < cutoff_time:
            user_calls.popleft()

    def _reset_daily_limits_if_needed(self, now: datetime):
        """Reset daily download limits if it's a new day"""

        current_date = now.date()
        if current_date != self.last_reset_date:
            logger.info(
                f"Resetting daily download limits for new day: {current_date}")
            self.daily_downloads.clear()
            self.last_reset_date = current_date

    def check_api_rate_limit(self, user_id: int) -> Tuple[bool, Dict]:
        """
        Check if user can make an API call
        Returns: (allowed, info_dict)
        """

        with self.lock:
            now = datetime.now(timezone.utc)

            # Clean up old calls
            self._cleanup_old_calls(user_id, now)

            # Check if under limit
            current_calls = len(self.api_calls[user_id])

            if current_calls < self.api_limit:
                # Allow the call and record it
                self.api_calls[user_id].append(now)

                remaining = self.api_limit - current_calls - 1
                reset_time = now + timedelta(seconds=self.api_window)

                return True, {
                    "allowed": True,
                    "remaining": remaining,
                    "reset_time": reset_time.isoformat(),
                    "limit": self.api_limit,
                    "window": self.api_window
                }
            else:
                # Rate limit exceeded
                oldest_call = self.api_calls[user_id][0]
                reset_time = oldest_call + timedelta(seconds=self.api_window)

                return False, {
                    "allowed": False,
                    "remaining": 0,
                    "reset_time": reset_time.isoformat(),
                    "limit": self.api_limit,
                    "window": self.api_window,
                    "message": f"Rate limit exceeded. Try again after {reset_time.strftime('%H:%M:%S')}"
                }

    def check_download_limit(self, user_id: int) -> Tuple[bool, Dict]:
        """
        Check if user can download images
        Returns: (allowed, info_dict)
        """

        with self.lock:
            now = datetime.now(timezone.utc)

            # Reset daily limits if needed
            self._reset_daily_limits_if_needed(now)

            current_downloads = self.daily_downloads.get(user_id, 0)

            if current_downloads < self.download_limit:
                return True, {
                    "allowed": True,
                    "remaining": self.download_limit - current_downloads,
                    "limit": self.download_limit,
                    "reset_time": (now + timedelta(days=1)).replace(hour=0, minute=0, second=0, microsecond=0).isoformat()
                }
            else:
                return False, {
                    "allowed": False,
                    "remaining": 0,
                    "limit": self.download_limit,
                    "reset_time": (now + timedelta(days=1)).replace(hour=0, minute=0, second=0, microsecond=0).isoformat(),
                    "message": f"Daily download limit exceeded. Try again tomorrow."
                }

    def record_download(self, user_id: int, count: int = 1) -> bool:
        """
        Record a download for the user
        Returns: True if successful, False if limit exceeded
        """

        with self.lock:
            now = datetime.now(timezone.utc)
            self._reset_daily_limits_if_needed(now)

            current_downloads = self.daily_downloads.get(user_id, 0)

            if current_downloads + count <= self.download_limit:
                self.daily_downloads[user_id] = current_downloads + count
                logger.info(
                    f"User {user_id} downloaded {count} images. Total today: {self.daily_downloads[user_id]}")
                return True
            else:
                logger.warning(
                    f"User {user_id} exceeded download limit. Requested: {count}, Current: {current_downloads}, Limit: {self.download_limit}")
                return False

    def get_user_stats(self, user_id: int) -> Dict:
        """Get current rate limit and download stats for a user"""

        with self.lock:
            now = datetime.now(timezone.utc)
            self._reset_daily_limits_if_needed(now)

            # API stats
            self._cleanup_old_calls(user_id, now)
            api_calls_count = len(self.api_calls[user_id])
            api_remaining = max(0, self.api_limit - api_calls_count)

            # Download stats
            downloads_count = self.daily_downloads.get(user_id, 0)
            downloads_remaining = max(0, self.download_limit - downloads_count)

            return {
                "api_calls": {
                    "used": api_calls_count,
                    "remaining": api_remaining,
                    "limit": self.api_limit,
                    "window_seconds": self.api_window
                },
                "downloads": {
                    "used": downloads_count,
                    "remaining": downloads_remaining,
                    "limit": self.download_limit,
                    "reset_time": (now + timedelta(days=1)).replace(hour=0, minute=0, second=0, microsecond=0).isoformat()
                }
            }

    def reset_user_limits(self, user_id: int):
        """Reset limits for a specific user (admin function)"""

        with self.lock:
            if user_id in self.api_calls:
                del self.api_calls[user_id]
            if user_id in self.daily_downloads:
                del self.daily_downloads[user_id]
            logger.info(f"Reset limits for user {user_id}")


# Global rate limit service instance
rate_limit_service = RateLimitService()
