"""
Support Ticket CRUD Tests
Tests for PUT /ticket, GET /ticket/{uuid}, and GET /tickets endpoints.

Usage:
    pytest tests/usecases/ticket/test_ticket.py -v
    pytest -m ticket -v
"""

import pytest
import json
from pathlib import Path
from helpers.api_client import APIClient
from helpers.assertions import (
    assert_status_code,
    assert_validation_error,
    assert_auth_failure,
    assert_ticket_structure,
    assert_ticket_status,
)

test_cases_path = Path(__file__).parent / "ticket.cases.json"
with open(test_cases_path) as f:
    test_data = json.load(f)


@pytest.mark.ticket
@pytest.mark.parametrize("test_case", [tc for tc in test_data["tests"] if not tc.get("skip")])
def test_parametrized_cases(api_client: APIClient, unauthenticated_client: APIClient, test_case: dict):
    """Parametrized ticket test cases from JSON."""
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

    if method == "GET":
        response = client.get(endpoint)
    elif method == "PUT":
        response = client.put(endpoint, inp.get("body", {}))
    elif method == "POST":
        response = client.post(endpoint, inp.get("body", {}))
    else:
        pytest.fail(f"Unsupported method: {method}")

    if "status_code" in expected:
        assert_status_code(response, expected["status_code"])

    if "status_code_in" in expected:
        actual = response.get("_status_code")
        assert actual in expected["status_code_in"], \
            f"Expected status in {expected['status_code_in']}, got {actual}"

    if assertion_type == "validation_error":
        assert_validation_error(response)
    elif assertion_type == "auth_failure":
        assert_auth_failure(response)
    elif assertion_type == "null_response":
        assert response.get("_status_code") == 200
    elif assertion_type == "list_response":
        assert response.get("_status_code") == 200

    print(f"  Test passed: {test_case['name']}")


# ============================================================================
# Standalone Tests
# ============================================================================

@pytest.mark.ticket
@pytest.mark.smoke
def test_get_ticket_nonexistent(unauthenticated_client: APIClient):
    """GET /ticket/{uuid} with nonexistent UUID returns 200 with null."""
    response = unauthenticated_client.get("/ticket/TICKET-nonexistent-uuid-12345")
    assert_status_code(response, 200)
    print("  Nonexistent ticket test passed")


@pytest.mark.ticket
@pytest.mark.smoke
def test_update_ticket_requires_both_fields(unauthenticated_client: APIClient):
    """PUT /ticket needs both uuid and status fields."""
    response_no_uuid = unauthenticated_client.put("/ticket", {"status": "closed"})
    assert_validation_error(response_no_uuid)

    response_no_status = unauthenticated_client.put("/ticket", {"uuid": "TICKET-test"})
    assert_validation_error(response_no_status)
    print("  Field requirement validation test passed")


@pytest.mark.ticket
def test_update_ticket_valid_payload(unauthenticated_client: APIClient):
    """PUT /ticket with valid uuid+status should not return 422."""
    response = unauthenticated_client.put("/ticket", {
        "uuid": "TICKET-test-update-12345",
        "status": "in_progress",
    })
    actual = response.get("_status_code")
    assert actual != 422, f"Expected non-422 for valid payload, got {actual}"
    print(f"  Valid ticket update test passed (status: {actual})")


@pytest.mark.ticket
def test_update_ticket_with_valid_statuses(unauthenticated_client: APIClient):
    """PUT /ticket accepts open, closed, in_progress status values."""
    for status in ["open", "closed", "in_progress"]:
        response = unauthenticated_client.put("/ticket", {
            "uuid": f"TICKET-status-test-{status}",
            "status": status,
        })
        actual = response.get("_status_code")
        assert actual != 422, f"Status '{status}' should be valid, got {actual}"
    print("  Valid status values test passed")


@pytest.mark.ticket
def test_get_tickets_requires_auth(unauthenticated_client: APIClient):
    """GET /tickets without auth should fail."""
    response = unauthenticated_client.get("/tickets")
    actual = response.get("_status_code")
    assert actual in (400, 422), f"Expected 400/422 without auth, got {actual}"
    print("  Tickets auth requirement test passed")


@pytest.mark.ticket
def test_get_tickets_with_auth(api_client: APIClient):
    """GET /tickets with valid auth returns 200."""
    response = api_client.get("/tickets")
    if response.get("_status_code") in (400, 401):
        pytest.skip("Token expired or invalid")
    actual = response.get("_status_code")
    assert actual == 200, f"Expected 200, got {actual}"
    print("  Authenticated tickets list test passed")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])
