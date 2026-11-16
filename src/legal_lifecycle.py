from dataclasses import dataclass
from datetime import datetime, timedelta, timezone


@dataclass(frozen=True)
class MatterObject:
    object_key: str
    kind: str
    created_at: datetime
    ttl_days: int


def expires_at(item: MatterObject) -> datetime:
    return item.created_at + timedelta(days=item.ttl_days)


def should_expire(item: MatterObject, now: datetime) -> bool:
    return now >= expires_at(item)


def lifecycle_rules() -> list[dict[str, object]]:
    return [{"action": "delete", "days": 30, "prefix": ""}]


def demo_intake() -> list[MatterObject]:
    created = datetime(2026, 1, 1, tzinfo=timezone.utc)
    return [
        MatterObject("matters/m-104/intake.json", "matter-intake", created, 30),
        MatterObject("matters/m-104/signed-delivery.pdf", "signed-document", created, 30),
        MatterObject("matters/m-104/deadline-follow-up.json", "deadline-follow-up", created, 30),
    ]
