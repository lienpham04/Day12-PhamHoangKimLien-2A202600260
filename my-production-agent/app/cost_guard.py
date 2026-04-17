import time
import logging
from dataclasses import dataclass, field
from fastapi import HTTPException
from .config import settings

logger = logging.getLogger(__name__)

@dataclass
class UserUsage:
    user_id: str
    month: str
    total_cost: float = 0.0

class CostGuard:
    def __init__(self, monthly_budget: float = 10.0):
        self.monthly_budget = monthly_budget
        self._usage_db = {} # Should be Redis in production

    def _get_usage(self, user_id: str) -> UserUsage:
        month = time.strftime("%Y-%m")
        key = f"{user_id}:{month}"
        if key not in self._usage_db:
            self._usage_db[key] = UserUsage(user_id=user_id, month=month)
        return self._usage_db[key]

    def check_budget(self, user_id: str):
        usage = self._get_usage(user_id)
        if usage.total_cost >= self.monthly_budget:
            raise HTTPException(
                status_code=402,
                detail=f"Monthly budget of ${self.monthly_budget} exceeded for user {user_id}."
            )

    def record_cost(self, user_id: str, cost: float):
        usage = self._get_usage(user_id)
        usage.total_cost += cost
        logger.info(f"Recorded cost ${cost:.4f} for {user_id}. Total this month: ${usage.total_cost:.4f}")

cost_guard = CostGuard(monthly_budget=settings.MONTHLY_BUDGET_USD)

def check_budget_dependency(user_id: str):
    cost_guard.check_budget(user_id)
