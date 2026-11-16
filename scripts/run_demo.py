import sys
from pathlib import Path

from datetime import datetime, timezone

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from src.infrai_client import InfraiClient
from src.legal_lifecycle import demo_intake, lifecycle_rules, should_expire


BUCKET = "legal-throwaways"
SWEEP_URL = "https://example.com/tasks/legal-lifecycle-sweep"


def main() -> None:
    client = InfraiClient()
    client.create_bucket(BUCKET)
    client.set_lifecycle(BUCKET, lifecycle_rules())
    cron = client.create_cron("0 * * * *", SWEEP_URL)
    now = datetime(2026, 2, 1, tzinfo=timezone.utc)
    expired = [item.object_key for item in demo_intake() if should_expire(item, now)]
    print({"bucket": BUCKET, "expired": expired, "job_id": cron.get("job_id") if isinstance(cron, dict) else cron})


if __name__ == "__main__":
    main()
