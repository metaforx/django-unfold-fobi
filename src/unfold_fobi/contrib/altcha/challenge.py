"""ALTCHA challenge generation and solution verification."""

from datetime import datetime, timedelta, timezone

from django.core.cache import caches

from . import conf


def create_challenge():
    """Generate a fresh ALTCHA challenge dict for the frontend."""
    import altcha

    expires = datetime.now(timezone.utc) + timedelta(seconds=conf.get_challenge_expiry())
    challenge = altcha.create_challenge_v1(
        hmac_key=conf.get_hmac_secret(),
        max_number=conf.get_max_number(),
        algorithm=conf.get_algorithm(),
        expires=expires,
    )
    return challenge.to_dict()


def verify_payload(payload_b64):
    """Verify a base64-encoded ALTCHA solution payload.

    Returns ``(True, None)`` on success or ``(False, error_message)`` on failure.
    """
    import altcha

    if not payload_b64:
        return False, "Missing ALTCHA payload."

    try:
        is_valid, error = altcha.verify_solution_v1(
            payload_b64,
            conf.get_hmac_secret(),
            check_expires=True,
        )
    except Exception:
        return False, "Invalid ALTCHA payload."

    if not is_valid:
        return False, error or "Invalid ALTCHA payload."

    # Replay protection
    cache = caches[conf.get_cache_alias()]
    cache_key = f"altcha:replay:{payload_b64[:64]}"
    if cache.get(cache_key):
        return False, "ALTCHA payload already used."
    cache.set(cache_key, 1, conf.get_challenge_expiry() * 2)

    return True, None
