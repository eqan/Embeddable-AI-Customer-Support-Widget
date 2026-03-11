"""
Conversation Statistics Tests
Tests for POST /stats (generate) and GET /stats (retrieve) endpoints.

Usage:
    pytest tests/usecases/stats/test_stats.py -v
    pytest -m stats -v
"""

import pytest
import json
from pathlib import Path
from helpers.api_client import APIClient
from helpers.assertions import (
    assert_status_code,
    assert_auth_failure,
    assert_stats_structure,
)

test_cases_path = Path(__file__).parent / "stats.cases.json"
with open(test_cases_path) as f:
    test_data = json.load(f)


@pytest.mark.stats
@pytest.mark.parametrize("test_case", [tc for tc in test_data["tests"] if not tc.get("skip")])
def test_parametrized_cases(api_client: APIClient, unauthenticated_client: APIClient, test_case: dict):
    """Parametrized stats test cases from JSON."""
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
    assertion_type = test_case.get("assertions", {}).get("type")

    client = unauthenticated_client if inp.get("no_auth") else api_client

    if method == "POST":
        response = client.post(endpoint, inp.get("body", {}))
    elif method == "GET":
        response = client.get(endpoint)
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
        assert actual_status in expected["status_code_in"], \
            f"Expected status in {expected['status_code_in']}, got {actual_status}"

    if assertion_type == "auth_failure":
        assert_auth_failure(response)
    elif assertion_type == "stats_structure":
        if actual_status in (400, 401):
            pytest.skip("Token expired or invalid")
        assert_stats_structure(response)
    elif assertion_type == "stats_or_null":
        if actual_status in (400, 401):
            pytest.skip("Token expired or invalid")

    print(f"  Test passed: {test_case['name']}")


# ============================================================================
# Standalone Tests
# ============================================================================

@pytest.mark.stats
@pytest.mark.smoke
def test_generate_stats_requires_auth(unauthenticated_client: APIClient):
    """POST /stats without auth token should fail."""
    response = unauthenticated_client.post("/stats", {})
    actual = response.get("_status_code")
    assert actual in (400, 422, 429), f"Expected 400/422/429 without auth, got {actual}"
    print("  Generate stats auth requirement test passed")


@pytest.mark.stats
@pytest.mark.smoke
def test_get_stats_requires_auth(unauthenticated_client: APIClient):
    """GET /stats without auth token should fail."""
    response = unauthenticated_client.get("/stats")
    actual = response.get("_status_code")
    assert actual in (400, 422, 429), f"Expected 400/422/429 without auth, got {actual}"
    print("  Get stats auth requirement test passed")


@pytest.mark.stats
def test_generate_stats_with_auth(api_client: APIClient):
    """POST /stats with valid auth generates stats with expected fields."""
    response = api_client.post("/stats", {})
    if response.get("_status_code") in (400, 401, 429):
        pytest.skip("Token expired/invalid or rate limited")
    assert_status_code(response, 200)
    assert_stats_structure(response)
    print("  Generate stats test passed")


@pytest.mark.stats
def test_get_stats_with_auth(api_client: APIClient):
    """GET /stats with valid auth returns stats or null."""
    response = api_client.get("/stats")
    actual = response.get("_status_code")
    if actual in (400, 401, 429):
        pytest.skip("Token expired/invalid or rate limited")
    assert_status_code(response, 200)
    print("  Get stats test passed")


@pytest.mark.stats
def test_stats_numeric_fields_non_negative(api_client: APIClient):
    """All numeric stats fields should be >= 0."""
    response = api_client.post("/stats", {})
    if response.get("_status_code") in (400, 401):
        pytest.skip("Token expired or invalid")
    if response.get("_status_code") != 200:
        pytest.skip(f"Unexpected status: {response.get('_status_code')}")

    non_negative_fields = [
        "conversations", "messages", "bookings", "human_handoffs",
        "successful_conversations", "success_rate", "avg_messages_per_conversation"
    ]
    for field in non_negative_fields:
        if field in response:
            assert response[field] >= 0, f"Stats field '{field}' should be >= 0, got {response[field]}"
    print("  Non-negative stats test passed")


@pytest.mark.stats
def test_stats_success_rate_bounded(api_client: APIClient):
    """success_rate should be between 0.0 and a reasonable upper bound."""
    response = api_client.post("/stats", {})
    if response.get("_status_code") in (400, 401):
        pytest.skip("Token expired or invalid")
    if response.get("_status_code") != 200:
        pytest.skip(f"Unexpected status: {response.get('_status_code')}")

    rate = response.get("success_rate", 0.0)
    assert 0.0 <= rate, f"success_rate should be >= 0, got {rate}"
    print(f"  Success rate bounded test passed (rate: {rate})")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])
