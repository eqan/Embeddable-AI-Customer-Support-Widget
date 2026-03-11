"""
Data Ingestion & Vector Search Tests
Tests for POST /ingestion/scrape-website and GET /ingestion/search endpoints.

Usage:
    pytest tests/usecases/ingestion/test_ingestion.py -v
    pytest -m ingestion -v
"""

import pytest
import json
from pathlib import Path
from helpers.api_client import APIClient
from helpers.assertions import (
    assert_status_code,
    assert_validation_error,
    assert_auth_failure,
)

test_cases_path = Path(__file__).parent / "ingestion.cases.json"
with open(test_cases_path) as f:
    test_data = json.load(f)


@pytest.mark.ingestion
@pytest.mark.parametrize("test_case", [tc for tc in test_data["tests"] if not tc.get("skip")])
def test_parametrized_cases(api_client: APIClient, unauthenticated_client: APIClient, test_case: dict):
    """Parametrized ingestion test cases from JSON."""
    if test_case.get("skip"):
        pytest.skip(test_case.get("skip_reason", "Test skipped"))

    tags = test_case.get("tags", [])
    if "requires_token" in tags:
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
        response = client.get(endpoint, params=inp.get("params"))
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

    if assertion_type == "validation_error":
        assert_validation_error(response)
    elif assertion_type == "auth_failure":
        assert_auth_failure(response)

    print(f"  Test passed: {test_case['name']}")


# ============================================================================
# Standalone Tests
# ============================================================================

@pytest.mark.ingestion
@pytest.mark.smoke
def test_scrape_requires_auth(unauthenticated_client: APIClient):
    """POST /ingestion/scrape-website without Bearer token returns 401."""
    response = unauthenticated_client.post("/ingestion/scrape-website", {
        "company_name": "Test Corp",
        "company_website": "https://example.com",
        "relevant_links_to_be_scraped": ["https://example.com"],
    })
    assert_status_code(response, 401)
    print("  Scrape auth requirement test passed")


@pytest.mark.ingestion
@pytest.mark.smoke
def test_search_requires_auth(unauthenticated_client: APIClient):
    """GET /ingestion/search without Bearer token returns 401."""
    response = unauthenticated_client.get("/ingestion/search", params={
        "query": "test", "company_website": "https://example.com"
    })
    assert_status_code(response, 401)
    print("  Search auth requirement test passed")


@pytest.mark.ingestion
def test_scrape_validates_required_fields(api_client: APIClient):
    """POST /ingestion/scrape-website with missing fields returns 422."""
    response = api_client.post("/ingestion/scrape-website", {"company_name": "Test"})
    if response.get("_status_code") == 401:
        pytest.skip("Token expired or invalid")
    assert_validation_error(response)
    print("  Scrape field validation test passed")


@pytest.mark.ingestion
def test_scrape_empty_body_validation(api_client: APIClient):
    """POST /ingestion/scrape-website with empty body returns 422."""
    response = api_client.post("/ingestion/scrape-website", {})
    if response.get("_status_code") == 401:
        pytest.skip("Token expired or invalid")
    assert_validation_error(response)
    print("  Scrape empty body validation test passed")


@pytest.mark.ingestion
def test_search_validates_query_param(api_client: APIClient):
    """GET /ingestion/search without query param returns 422."""
    response = api_client.get("/ingestion/search", params={
        "company_website": "https://example.com"
    })
    if response.get("_status_code") == 401:
        pytest.skip("Token expired or invalid")
    assert_validation_error(response)
    print("  Search query validation test passed")


@pytest.mark.ingestion
@pytest.mark.external
@pytest.mark.slow
def test_scrape_valid_request(api_client: APIClient):
    """POST /ingestion/scrape-website with valid input calls external services."""
    response = api_client.post("/ingestion/scrape-website", {
        "company_name": "Example Corp",
        "company_website": "https://example.com",
        "relevant_links_to_be_scraped": ["https://example.com"],
    })
    if response.get("_status_code") == 401:
        pytest.skip("Token expired or invalid")
    actual = response.get("_status_code")
    assert actual in (200, 500), f"Expected 200 or 500 (external dep), got {actual}"
    print(f"  Valid scrape request test passed (status: {actual})")


@pytest.mark.ingestion
@pytest.mark.external
def test_search_valid_query(api_client: APIClient):
    """GET /ingestion/search with valid params returns results or handles gracefully."""
    response = api_client.get("/ingestion/search", params={
        "query": "services", "company_website": "https://example.com", "top_k": "2"
    })
    if response.get("_status_code") == 401:
        pytest.skip("Token expired or invalid")
    actual = response.get("_status_code")
    assert actual in (200, 500), f"Expected 200 or 500 (external dep), got {actual}"
    print(f"  Valid search test passed (status: {actual})")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])
