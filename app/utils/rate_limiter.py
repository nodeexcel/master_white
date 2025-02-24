from datetime import datetime, timedelta
from typing import Dict
import time

class RateLimiter:
    def __init__(self, max_requests: int, time_window: int):
        self.max_requests = max_requests
        self.time_window = time_window  # in seconds
        self.requests = {}
        
    def can_proceed(self, user_id: str) -> bool:
        now = datetime.now()
        self._cleanup_old_requests(now)
        
        if user_id not in self.requests:
            self.requests[user_id] = []
            
        if len(self.requests[user_id]) < self.max_requests:
            self.requests[user_id].append(now)
            return True
            
        return False
        
    def _cleanup_old_requests(self, now: datetime):
        cutoff = now - timedelta(seconds=self.time_window)
        for user_id in list(self.requests.keys()):
            self.requests[user_id] = [
                req_time for req_time in self.requests[user_id]
                if req_time > cutoff
            ] 