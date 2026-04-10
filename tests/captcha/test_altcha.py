"""T25: ALTCHA backend integration tests."""

import base64
import json

import pytest

ALTCHA_SECRET = "test-altcha-secret-key-for-testing"


def _make_valid_payload(secret=ALTCHA_SECRET):
    """Create a valid ALTCHA challenge, solve it, return base64 payload."""
    import altcha

    ch = altcha.create_challenge_v1(hmac_key=secret, max_number=100)
    sol = altcha.solve_challenge_v1(ch.challenge, ch.salt, ch.algorithm, ch.max_number)
    payload_dict = {
        "algorithm": ch.algorithm,
        "challenge": ch.challenge,
        "number": sol.number,
        "salt": ch.salt,
        "signature": ch.signature,
    }
    return base64.b64encode(json.dumps(payload_dict).encode()).decode()


class TestDisabledMode:
    """Without ALTCHA configured, everything works as before."""

    def test_form_fields_no_altcha_field(self, admin_client, form_entry):
        response = admin_client.get(f"/api/fobi-form-fields/{form_entry.slug}/")
        assert response.status_code == 200
        names = [f["name"] for f in response.json()["fields"]]
        assert "altcha" not in names

    def test_submission_works_without_altcha(self, admin_client, form_entry):
        response = admin_client.put(
            f"/api/fobi-form-entry/{form_entry.slug}/",
            data=json.dumps({"full_name": "Test"}),
            content_type="application/json",
        )
        assert response.status_code == 200

    def test_base_package_import_safe(self):
        """Base unfold_fobi has no hard altcha dependency."""
        import pathlib

        base_pkg = pathlib.Path(__file__).resolve().parent.parent.parent / "src" / "unfold_fobi"
        violations = [
            f"{py.relative_to(base_pkg)}"
            for py in base_pkg.rglob("*.py")
            if "contrib" not in py.parts
            and any(line.startswith(("from altcha", "import altcha")) for line in py.read_text().splitlines())
        ]
        assert not violations, f"Hard altcha imports in base package: {violations}"


class TestEnabledFormFields:
    """With ALTCHA configured, form-fields response includes the field."""

    def test_form_fields_includes_altcha(self, settings, admin_client, form_entry):
        settings.UNFOLD_FOBI_ALTCHA_HMAC_SECRET = ALTCHA_SECRET
        settings.INSTALLED_APPS = list(settings.INSTALLED_APPS) + ["unfold_fobi.contrib.altcha"]

        response = admin_client.get(f"/api/fobi-form-fields/{form_entry.slug}/")
        assert response.status_code == 200
        names = [f["name"] for f in response.json()["fields"]]
        assert "altcha" in names

        altcha_field = [f for f in response.json()["fields"] if f["name"] == "altcha"][0]
        assert altcha_field["type"] == "AltchaField"
        assert altcha_field["widget"] == "AltchaWidget"
        assert altcha_field["required"] is True


class TestChallengeGeneration:
    """Challenge endpoint returns valid ALTCHA challenges."""

    def test_challenge_shape(self, settings):
        settings.UNFOLD_FOBI_ALTCHA_HMAC_SECRET = ALTCHA_SECRET
        from unfold_fobi.contrib.altcha.challenge import create_challenge

        ch = create_challenge()
        assert "algorithm" in ch
        assert "challenge" in ch
        assert "salt" in ch
        assert "signature" in ch
        assert "maxNumber" in ch

    def test_challenge_solvable(self, settings):
        settings.UNFOLD_FOBI_ALTCHA_HMAC_SECRET = ALTCHA_SECRET
        import altcha
        from unfold_fobi.contrib.altcha.challenge import create_challenge

        ch = create_challenge()
        sol = altcha.solve_challenge_v1(
            ch["challenge"], ch["salt"], ch["algorithm"], ch["maxNumber"]
        )
        assert sol is not None
        assert sol.number >= 0


class TestVerification:
    """Payload verification: valid, invalid, expired, replayed."""

    def test_valid_payload_passes(self, settings):
        settings.UNFOLD_FOBI_ALTCHA_HMAC_SECRET = ALTCHA_SECRET
        from unfold_fobi.contrib.altcha.challenge import verify_payload

        payload = _make_valid_payload()
        ok, err = verify_payload(payload)
        assert ok is True
        assert err is None

    def test_missing_payload_fails(self, settings):
        settings.UNFOLD_FOBI_ALTCHA_HMAC_SECRET = ALTCHA_SECRET
        from unfold_fobi.contrib.altcha.challenge import verify_payload

        ok, err = verify_payload(None)
        assert ok is False

    def test_invalid_payload_fails(self, settings):
        settings.UNFOLD_FOBI_ALTCHA_HMAC_SECRET = ALTCHA_SECRET
        from unfold_fobi.contrib.altcha.challenge import verify_payload

        ok, err = verify_payload("not-valid-base64-payload")
        assert ok is False

    def test_replay_rejected(self, settings):
        settings.UNFOLD_FOBI_ALTCHA_HMAC_SECRET = ALTCHA_SECRET
        from unfold_fobi.contrib.altcha.challenge import verify_payload

        payload = _make_valid_payload()
        ok1, _ = verify_payload(payload)
        assert ok1 is True

        ok2, err2 = verify_payload(payload)
        assert ok2 is False
        assert "already used" in err2

    def test_wrong_secret_fails(self, settings):
        settings.UNFOLD_FOBI_ALTCHA_HMAC_SECRET = "wrong-secret"
        from unfold_fobi.contrib.altcha.challenge import verify_payload

        payload = _make_valid_payload()  # signed with ALTCHA_SECRET
        ok, err = verify_payload(payload)
        assert ok is False
