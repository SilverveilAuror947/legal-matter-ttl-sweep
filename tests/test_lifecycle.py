from datetime import datetime, timezone

from src.legal_lifecycle import MatterObject, should_expire


def test_signed_delivery_is_expired_at_the_ttl_boundary() -> None:
    created = datetime(2026, 1, 1, tzinfo=timezone.utc)
    document = MatterObject("matters/m-104/signed-delivery.pdf", "signed-document", created, 30)

    assert should_expire(document, datetime(2026, 1, 31, tzinfo=timezone.utc))
    assert not should_expire(document, datetime(2026, 1, 30, 23, 59, tzinfo=timezone.utc))
