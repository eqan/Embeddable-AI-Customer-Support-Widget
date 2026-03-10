"""
Health & Root Endpoint Tests
Tests the root health-check endpoint and basic server availability.

Usage:
    pytest tests/usecases/health/test_health.py -v
    pytest -m health -v
"""

import pytest
import json
from pathlib import Path
from helpers.api_client import APIClient
from helpers.assertions import (
    assert_status_code,
    assert_field_exists,
    assert_contains,
)

test_cases_path = Path(__file__).parent / "health.cases.json"
with open(test_cases_path) as f:
    test_data = json.load(f)


@pytest.mark.health
@pytest.mark.smoke
@pytest.mark.parametrize("test_case", [tc for tc in test_data["tests"] if not tc.get("skip")])
def test_parametrized_cases(unauthenticated_client: APIClient, test_case: dict):
    """Parametrized test running all health check cases from JSON."""
    if test_case.get("skip"):
        pytest.skip(test_case.get("skip_reason", "Test skipped"))

    print(f"\n  Running: {test_case['name']}")
    print(f"  Description: {test_case['description']}")

    method = test_case["input"]["method"]
    endpoint = test_case["input"]["endpoint"]

    if method == "GET":
        response = unauthenticated_client.get(endpoint)
    else:
        response = unauthenticated_client.post(endpoint, {})

    expected = test_case["expected"]
    assertion = test_case.get("assertions", {})
    assertion_type = assertion.get("type")

    if "status_code" in expected:
        assert_status_code(response, expected["status_code"])

    if "status_code_in" in expected:
        actual = response.get("_status_code")
        assert actual in expected["status_code_in"], \
            f"Expected status in {expected['status_code_in']}, got {actual}"

    if expected.get("has_field"):
        assert_field_exists(response, expected["has_field"])

    if assertion_type == "field_contains":
        assert_contains(response, assertion["field"], assertion["substring"])

    if assertion_type == "content_type":
        headers = response.get("_headers", {})
        ct = headers.get("content-type", "")
        assert expected["content_type_contains"] in ct, \
            f"Expected content-type containing '{expected['content_type_contains']}', got '{ct}'"

    print(f"  Test passed: {test_case['name']}")


@pytest.mark.health
@pytest.mark.smoke
def test_root_returns_running_message(unauthenticated_client: APIClient):
    """Standalone: GET / returns a message indicating the API is running."""
    response = unauthenticated_client.get("/")
    assert_status_code(response, 200)
    assert_field_exists(response, "message")
    assert "running" in response["message"].lower(), \
        f"Expected 'running' in message, got: {response['message']}"
    print("  Root endpoint test passed")


@pytest.mark.health
@pytest.mark.smoke
def test_server_is_reachable(unauthenticated_client: APIClient):
    """Standalone: verify the server is reachable and not returning connection errors."""
    response = unauthenticated_client.get("/")
    assert response.get("_status_code") != 503, "Server is unreachable (503)"
    assert "error" not in response or "Connection error" not in response.get("error", ""), \
        f"Connection error: {response.get('error')}"
    print("  Server reachability test passed")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])
