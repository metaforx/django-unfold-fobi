"""T25: ALTCHA backend integration tests."""

import base64
import json

import pytest

altcha = pytest.importorskip("altcha", reason="altcha package not installed")

ALTCHA_SECRET = "test-altcha-secret-key-for-testing"


def _make_valid_payload(secret=ALTCHA_SECRET):
    """Create a valid ALTCHA challenge, solve it, return base64 payload."""
    challenge = altcha.create_challenge_v1(hmac_key=secret, max_number=100)
    solution = altcha.solve_challenge_v1(challenge.challenge, challenge.salt, challenge.algorithm, challenge.max_number)
    payload_dict = {
        "algorithm": challenge.algorithm,
        "challenge": challenge.challenge,
        "number": solution.number,
        "salt": challenge.salt,
        "signature": challenge.signature,
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
        from unfold_fobi.contrib.altcha.challenge import create_challenge

        challenge = create_challenge()
        solution = altcha.solve_challenge_v1(
            challenge["challenge"], challenge["salt"], challenge["algorithm"], challenge["maxNumber"]
        )
        assert solution is not None
        assert solution.number >= 0


class TestVerification:
    """Payload verification: valid, invalid, expired, replayed."""

    def test_valid_payload_passes(self, settings):
        settings.UNFOLD_FOBI_ALTCHA_HMAC_SECRET = ALTCHA_SECRET
        from unfold_fobi.contrib.altcha.challenge import verify_payload

        payload = _make_valid_payload()
        is_valid, error = verify_payload(payload)
        assert is_valid is True
        assert error is None

    def test_missing_payload_fails(self, settings):
        settings.UNFOLD_FOBI_ALTCHA_HMAC_SECRET = ALTCHA_SECRET
        from unfold_fobi.contrib.altcha.challenge import verify_payload

        is_valid, error = verify_payload(None)
        assert is_valid is False

    def test_invalid_payload_fails(self, settings):
        settings.UNFOLD_FOBI_ALTCHA_HMAC_SECRET = ALTCHA_SECRET
        from unfold_fobi.contrib.altcha.challenge import verify_payload

        is_valid, error = verify_payload("not-valid-base64-payload")
        assert is_valid is False

    def test_replay_rejected(self, settings):
        settings.UNFOLD_FOBI_ALTCHA_HMAC_SECRET = ALTCHA_SECRET
        from unfold_fobi.contrib.altcha.challenge import verify_payload

        payload = _make_valid_payload()
        is_valid, _ = verify_payload(payload)
        assert is_valid is True

        is_valid, error = verify_payload(payload)
        assert is_valid is False
        assert "already used" in error

    def test_wrong_secret_fails(self, settings):
        settings.UNFOLD_FOBI_ALTCHA_HMAC_SECRET = "wrong-secret"
        from unfold_fobi.contrib.altcha.challenge import verify_payload

        payload = _make_valid_payload()  # signed with ALTCHA_SECRET
        is_valid, error = verify_payload(payload)
        assert is_valid is False
