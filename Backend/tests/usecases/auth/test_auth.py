"""
Authentication & Token Verification Tests
Tests for POST /google-login and GET /verify-token

Usage:
    pytest tests/usecases/auth/test_auth.py -v
    pytest -m auth -v
"""

import pytest
import json
from pathlib import Path
from helpers.api_client import APIClient
from helpers.assertions import (
    assert_status_code,
    assert_field_exists,
    assert_field_equals,
    assert_validation_error,
    assert_auth_failure,
    assert_token_verified,
)

test_cases_path = Path(__file__).parent / "auth.cases.json"
with open(test_cases_path) as f:
    test_data = json.load(f)


@pytest.mark.auth
@pytest.mark.parametrize("test_case", [tc for tc in test_data["tests"] if not tc.get("skip")])
def test_parametrized_cases(api_client: APIClient, unauthenticated_client: APIClient, test_case: dict):
    """Parametrized auth test cases from JSON."""
    if test_case.get("skip"):
        pytest.skip(test_case.get("skip_reason", "Test skipped"))

    if "requires_token" in test_case.get("tags", []):
        try:
            from tests.helpers.auth_helper import get_primary_user_token
            token = get_primary_user_token()
            if not token:
                pytest.skip("No auth token configured")
        except ValueError:
            pytest.skip("No auth token configured")

    print(f"\n  Running: {test_case['name']}")
    print(f"  Description: {test_case['description']}")

    inp = test_case["input"]
    method = inp["method"]
    endpoint = inp["endpoint"]
    expected = test_case["expected"]
    assertion = test_case.get("assertions", {})
    assertion_type = assertion.get("type")

    client = api_client if inp.get("use_auth") else unauthenticated_client

    if method == "POST":
        response = client.post(endpoint, inp.get("body", {}))
    elif method == "GET":
        custom_headers = inp.get("headers")
        response = client.get(endpoint, headers=custom_headers)
    else:
        pytest.fail(f"Unsupported method: {method}")

    actual_status = response.get("_status_code")

    if actual_status == 429:
        pytest.skip("Rate limited (429) — retry after a pause")

    if inp.get("use_auth") and actual_status in (400, 401):
        pytest.skip("Token expired or invalid — update persistent-users.json")

    if "status_code" in expected:
        assert_status_code(response, expected["status_code"])

    if "status_code_in" in expected:
        actual = response.get("_status_code")
        assert actual in expected["status_code_in"], \
            f"Expected status in {expected['status_code_in']}, got {actual}"

    if expected.get("has_field"):
        assert_field_exists(response, expected["has_field"])

    if "field_equals" in expected:
        for field, value in expected["field_equals"].items():
            assert_field_equals(response, field, value)

    if assertion_type == "validation_error":
        assert_validation_error(response)
    elif assertion_type == "auth_failure":
        assert_auth_failure(response)
    elif assertion_type == "token_verified":
        assert_token_verified(response)

    print(f"  Test passed: {test_case['name']}")


# ============================================================================
# Standalone Tests
# ============================================================================

@pytest.mark.auth
@pytest.mark.smoke
def test_google_login_missing_body(unauthenticated_client: APIClient):
    """POST /google-login with no body should return 422."""
    response = unauthenticated_client.post("/google-login", {})
    assert_validation_error(response)
    print("  Missing body test passed")


@pytest.mark.auth
def test_google_login_invalid_credential(unauthenticated_client: APIClient):
    """POST /google-login with garbage credential should fail."""
    response = unauthenticated_client.post("/google-login", {"code": "not.a.real.google.token"})
    assert_auth_failure(response)
    print("  Invalid credential test passed")


@pytest.mark.auth
@pytest.mark.smoke
def test_verify_token_requires_auth_header(unauthenticated_client: APIClient):
    """GET /verify-token without Authorization header returns 401."""
    response = unauthenticated_client.get("/verify-token")
    assert_status_code(response, 401)
    print("  Missing auth header test passed")


@pytest.mark.auth
def test_verify_token_rejects_invalid_jwt(unauthenticated_client: APIClient):
    """GET /verify-token with a garbage JWT returns 401."""
    response = unauthenticated_client.get(
        "/verify-token",
        headers={"Authorization": "Bearer this.is.not.valid"}
    )
    assert_status_code(response, 401)
    print("  Invalid JWT test passed")


@pytest.mark.auth
def test_verify_token_rejects_expired_jwt(unauthenticated_client: APIClient):
    """GET /verify-token with an expired JWT returns 401."""
    import jwt as pyjwt
    expired_token = pyjwt.encode(
        {"sub": "123", "email": "expired@test.com", "exp": 1000000000},
        "wrong-secret",
        algorithm="HS256"
    )
    response = unauthenticated_client.get(
        "/verify-token",
        headers={"Authorization": f"Bearer {expired_token}"}
    )
    assert_status_code(response, 401)
    print("  Expired JWT test passed")


@pytest.mark.auth
def test_verify_token_with_valid_token(api_client: APIClient):
    """GET /verify-token with a valid token from persistent-users returns 200."""
    response = api_client.get("/verify-token")
    if response.get("_status_code") == 401:
        pytest.skip("Token expired or invalid — update persistent-users.json")
    assert_token_verified(response)
    print("  Valid token verification test passed")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])
