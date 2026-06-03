"""
Usage tracking helpers for the pkgprobe production API.

Records endpoint calls in the database and provides per-customer usage summaries.
"""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Optional

from .api_db import ApiKey, UsageRecord


def record_usage(db_session, *, api_key_id: int, endpoint: str) -> None:
    """Insert a usage record for an endpoint call."""
    record = UsageRecord(
        api_key_id=api_key_id,
        endpoint=endpoint,
        timestamp=datetime.now(timezone.utc),
    )
    db_session.add(record)
    db_session.commit()


def get_usage_summary(
    db_session,
    *,
    customer_id: int,
    since: Optional[datetime] = None,
) -> dict[str, int]:
    """Get usage counts by endpoint for a customer."""
    from sqlalchemy import func

    results = (
        db_session.query(UsageRecord.endpoint, func.count(UsageRecord.id))
        .join(ApiKey, ApiKey.id == UsageRecord.api_key_id)
        .filter(ApiKey.customer_id == customer_id)
        .group_by(UsageRecord.endpoint)
    )
    if since:
        results = results.filter(UsageRecord.timestamp >= since)

    return {row[0]: row[1] for row in results.all()}
