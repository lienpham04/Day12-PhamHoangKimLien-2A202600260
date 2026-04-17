import time
import logging
from dataclasses import dataclass, field
from fastapi import HTTPException

logger = logging.getLogger(__name__)

@dataclass
class UsageRecord:
    user_id: str
    cost_usd: float = 0.0
    day: str = field(default_factory=lambda: time.strftime("%Y-%m-%d"))

class CostGuard:
    def __init__(self, daily_budget_usd: float = 1.0):
        self.daily_budget_usd = daily_budget_usd
        self._records: dict[str, UsageRecord] = {}

    def _get_record(self, user_id: str) -> UsageRecord:
        today = time.strftime("%Y-%m-%d")
        record = self._records.get(user_id)
        if not record or record.day != today:
            self._records[user_id] = UsageRecord(user_id=user_id, day=today)
        return self._records[user_id]

    def check_budget(self, user_id: str) -> None:
        record = self._get_record(user_id)
        if record.cost_usd >= self.daily_budget_usd:
            raise HTTPException(
                status_code=402,
                detail=f"Budget exceeded for user {user_id}. Daily limit: ${self.daily_budget_usd}"
            )

    def record_usage(self, user_id: str, cost: float):
        record = self._get_record(user_id)
        record.cost_usd += cost
        logger.info(f"Recorded cost ${cost:.4f} for user {user_id}. Total: ${record.cost_usd:.4f}")

# Singleton instance
cost_guard = CostGuard(daily_budget_usd=1.0)
