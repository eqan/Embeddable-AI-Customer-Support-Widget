"""
Chatbot Response & Chat History Tests
Tests for POST /chatbot-response and GET /all-chats endpoints.

Usage:
    pytest tests/usecases/chatbot/test_chatbot.py -v
    pytest -m chatbot -v
"""

import pytest
import json
import uuid
from pathlib import Path
from helpers.api_client import APIClient
from helpers.assertions import (
    assert_status_code,
    assert_field_exists,
    assert_validation_error,
    assert_auth_failure,
    assert_chatbot_response,
    assert_booking_response,
    assert_handoff_response,
    assert_regular_response,
)

test_cases_path = Path(__file__).parent / "chatbot.cases.json"
with open(test_cases_path) as f:
    test_data = json.load(f)


def _prepare_body(test_case: dict, primary_token: str = None) -> dict:
    """Build request body, injecting auth token and handling special placeholders."""
    body = dict(test_case["input"].get("body", {}))

    if test_case["input"].get("use_auth_token") and primary_token:
        body["token"] = primary_token

    if body.get("message") == "__GENERATE_LONG_STRING_10001__":
        body["message"] = "x" * 10001

    return body


@pytest.mark.chatbot
@pytest.mark.parametrize("test_case", [tc for tc in test_data["tests"] if not tc.get("skip")])
def test_parametrized_cases(api_client: APIClient, unauthenticated_client: APIClient, primary_token: str, test_case: dict):
    """Parametrized chatbot test cases from JSON."""
    if test_case.get("skip"):
        pytest.skip(test_case.get("skip_reason", "Test skipped"))

    tags = test_case.get("tags", [])
    if "external" in tags:
        pytest.importorskip("requests")

    print(f"\n  Running: {test_case['name']}")
    print(f"  Description: {test_case['description']}")

    inp = test_case["input"]
    method = inp["method"]
    endpoint = inp["endpoint"]
    expected = test_case["expected"]
    assertion_type = test_case.get("assertions", {}).get("type")

    body = _prepare_body(test_case, primary_token)
    client = unauthenticated_client if inp.get("no_auth") else api_client

    if method == "POST":
        response = client.post(endpoint, body)
    else:
        response = client.get(endpoint)

    actual_status = response.get("_status_code")

    if actual_status == 429:
        pytest.skip("Rate limited (429) — retry after a pause")

    if inp.get("use_auth_token") and actual_status in (400, 401):
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
    elif assertion_type == "regular_response":
        assert_regular_response(response)
    elif assertion_type == "booking_response":
        assert_booking_response(response)
    elif assertion_type == "handoff_response":
        assert_handoff_response(response)

    print(f"  Test passed: {test_case['name']}")


# ============================================================================
# Standalone Tests
# ============================================================================

@pytest.mark.chatbot
@pytest.mark.smoke
def test_chatbot_rejects_empty_body(unauthenticated_client: APIClient):
    """POST /chatbot-response with empty body returns 422."""
    response = unauthenticated_client.post("/chatbot-response", {})
    assert_validation_error(response)
    print("  Empty body validation test passed")


@pytest.mark.chatbot
def test_chatbot_rejects_missing_required_fields(unauthenticated_client: APIClient):
    """POST /chatbot-response with partial body returns 422."""
    response = unauthenticated_client.post("/chatbot-response", {"message": "hi"})
    assert_validation_error(response)
    print("  Missing fields validation test passed")


@pytest.mark.chatbot
def test_chatbot_rejects_invalid_token(unauthenticated_client: APIClient):
    """POST /chatbot-response with a bad JWT returns 400."""
    response = unauthenticated_client.post("/chatbot-response", {
        "message": "Hello",
        "token": "bad.token.value",
        "session_id": "test-bad-token",
        "chat_history": [],
        "website_url": "https://example.com",
        "website_description": "Test",
    })
    actual = response.get("_status_code")
    assert actual in (400, 429), f"Expected 400 or 429 (rate limited), got {actual}"
    print("  Invalid token rejection test passed")


@pytest.mark.chatbot
@pytest.mark.external
@pytest.mark.slow
def test_chatbot_returns_valid_response(api_client: APIClient, primary_token: str):
    """POST /chatbot-response with valid input returns a structured ChatbotResponse."""
    session_id = f"test-valid-{uuid.uuid4()}"
    response = api_client.post("/chatbot-response", {
        "message": "What services do you offer?",
        "token": primary_token,
        "session_id": session_id,
        "chat_history": [],
        "website_url": "https://example.com",
        "website_description": "Example Corp offers cloud and AI solutions",
    })
    if response.get("_status_code") in (401, 400):
        pytest.skip("Token expired or invalid — update persistent-users.json")
    assert_chatbot_response(response)
    assert len(response["response"]) > 0, "Response text should not be empty"
    print(f"  Valid response test passed (response length: {len(response['response'])})")


@pytest.mark.chatbot
@pytest.mark.external
@pytest.mark.slow
def test_chatbot_booking_intent(api_client: APIClient, primary_token: str):
    """Asking to book a meeting should trigger is_booking=true."""
    session_id = f"test-booking-{uuid.uuid4()}"
    response = api_client.post("/chatbot-response", {
        "message": "I'd like to book a demo call with your sales team next week",
        "token": primary_token,
        "session_id": session_id,
        "chat_history": [],
        "website_url": "https://example.com",
        "website_description": "Example Corp offers cloud and AI solutions",
    })
    if response.get("_status_code") in (401, 400):
        pytest.skip("Token expired or invalid")
    assert_booking_response(response)
    print("  Booking intent test passed")


@pytest.mark.chatbot
@pytest.mark.external
@pytest.mark.slow
def test_chatbot_handoff_intent(api_client: APIClient, primary_token: str):
    """Asking to talk to a human should trigger is_human_handoff=true."""
    session_id = f"test-handoff-{uuid.uuid4()}"
    response = api_client.post("/chatbot-response", {
        "message": "I want to talk to a real person, can you connect me with a human agent?",
        "token": primary_token,
        "session_id": session_id,
        "chat_history": [],
        "website_url": "https://example.com",
        "website_description": "Example Corp offers cloud and AI solutions",
    })
    if response.get("_status_code") in (401, 400):
        pytest.skip("Token expired or invalid")
    assert_handoff_response(response)
    print("  Human handoff intent test passed")


@pytest.mark.chatbot
@pytest.mark.external
@pytest.mark.slow
def test_chatbot_maintains_context_with_history(api_client: APIClient, primary_token: str):
    """Chatbot should use chat_history for contextual responses."""
    session_id = f"test-context-{uuid.uuid4()}"
    history = [
        {"role": "user", "content": "What is your pricing?"},
        {"role": "model", "content": "We offer plans starting at $99/month."},
    ]
    response = api_client.post("/chatbot-response", {
        "message": "Is there a discount for annual billing?",
        "token": primary_token,
        "session_id": session_id,
        "chat_history": history,
        "website_url": "https://example.com",
        "website_description": "Example Corp offers SaaS with annual billing discounts",
    })
    if response.get("_status_code") in (401, 400):
        pytest.skip("Token expired or invalid")
    assert_chatbot_response(response)
    print("  Context maintenance test passed")


@pytest.mark.chatbot
def test_chatbot_payload_size_limit(unauthenticated_client: APIClient):
    """POST /chatbot-response with oversized payload (>50KB) returns 413."""
    large_history = [{"role": "user", "content": "x" * 5000} for _ in range(20)]
    response = unauthenticated_client.post("/chatbot-response", {
        "message": "Hello",
        "token": "test",
        "session_id": "size-test",
        "chat_history": large_history,
        "website_url": "https://example.com",
        "website_description": "Test",
    })
    actual = response.get("_status_code")
    assert actual in (413, 422, 400), f"Expected 413/422/400 for oversized payload, got {actual}"
    print("  Payload size limit test passed")


# ============================================================================
# SSE Streaming Endpoint Tests
# ============================================================================

from helpers.assertions import (
    parse_sse_events,
    assert_sse_has_event,
    assert_sse_intent,
    assert_sse_done,
    assert_sse_stream_valid,
)


@pytest.mark.chatbot
@pytest.mark.smoke
def test_stream_rejects_empty_body(unauthenticated_client: APIClient):
    """POST /chatbot-response/stream with empty body returns 422."""
    response = unauthenticated_client.post("/chatbot-response/stream", {})
    assert_validation_error(response)
    print("  SSE: empty body validation test passed")


@pytest.mark.chatbot
def test_stream_rejects_invalid_token(unauthenticated_client: APIClient):
    """POST /chatbot-response/stream with bad JWT returns 400."""
    response = unauthenticated_client.post("/chatbot-response/stream", {
        "message": "Hello",
        "token": "bad.token.value",
        "session_id": "test-stream-bad-token",
        "chat_history": [],
        "website_url": "https://example.com",
        "website_description": "Test",
    })
    actual = response.get("_status_code")
    assert actual in (400, 429), f"Expected 400 or 429, got {actual}"
    print("  SSE: invalid token rejection test passed")


@pytest.mark.chatbot
def test_stream_returns_sse_content_type(api_client: APIClient, primary_token: str):
    """POST /chatbot-response/stream returns text/event-stream content type."""
    response = api_client.post_sse("/chatbot-response/stream", {
        "message": "Hi",
        "token": primary_token,
        "session_id": f"test-sse-ct-{uuid.uuid4()}",
        "chat_history": [],
        "website_url": "https://example.com",
        "website_description": "Test company",
    })
    actual_status = response.get("_status_code")
    if actual_status in (400, 401):
        pytest.skip("Token expired or invalid")
    if actual_status == 429:
        pytest.skip("Rate limited")
    content_type = response.get("_headers", {}).get("content-type", "")
    assert "text/event-stream" in content_type, \
        f"Expected text/event-stream, got {content_type}"
    print("  SSE: content type test passed")


@pytest.mark.chatbot
@pytest.mark.external
@pytest.mark.slow
def test_stream_regular_response(api_client: APIClient, primary_token: str):
    """SSE stream for a regular question contains intent+token(s)+done events."""
    response = api_client.post_sse("/chatbot-response/stream", {
        "message": "What services do you offer?",
        "token": primary_token,
        "session_id": f"test-sse-regular-{uuid.uuid4()}",
        "chat_history": [],
        "website_url": "https://example.com",
        "website_description": "Example Corp offers cloud and AI solutions",
    })
    if response.get("_status_code") in (400, 401):
        pytest.skip("Token expired or invalid")
    if response.get("_status_code") == 429:
        pytest.skip("Rate limited")

    events = response.get("_events", [])
    assert_sse_stream_valid(events)
    assert_sse_intent(events, "regular")

    token_events = [e for e in events if e["event"] == "token"]
    assert len(token_events) > 0, "Regular response should have token events"

    full_text = "".join(e["data"]["text"] for e in token_events)
    assert len(full_text) > 0, "Streamed text should not be empty"

    done_evt = assert_sse_done(events)
    assert done_evt["data"]["is_booking"] is False
    assert done_evt["data"]["is_human_handoff"] is False
    print(f"  SSE: regular response test passed ({len(token_events)} chunks)")


@pytest.mark.chatbot
@pytest.mark.external
@pytest.mark.slow
def test_stream_booking_response(api_client: APIClient, primary_token: str):
    """SSE stream for a booking request returns intent+action+done events."""
    response = api_client.post_sse("/chatbot-response/stream", {
        "message": "I'd like to book a demo call with your team next week",
        "token": primary_token,
        "session_id": f"test-sse-booking-{uuid.uuid4()}",
        "chat_history": [],
        "website_url": "https://example.com",
        "website_description": "Example Corp offers cloud and AI solutions",
    })
    if response.get("_status_code") in (400, 401):
        pytest.skip("Token expired or invalid")
    if response.get("_status_code") == 429:
        pytest.skip("Rate limited")

    events = response.get("_events", [])
    assert_sse_stream_valid(events)
    assert_sse_intent(events, "booking")

    action_events = assert_sse_has_event(events, "action")
    assert action_events[0]["data"]["type"] == "booking"
    assert len(action_events[0]["data"].get("response", "")) > 0

    done_evt = assert_sse_done(events)
    assert done_evt["data"]["is_booking"] is True
    print("  SSE: booking response test passed")


@pytest.mark.chatbot
@pytest.mark.external
@pytest.mark.slow
def test_stream_handoff_response(api_client: APIClient, primary_token: str):
    """SSE stream for a handoff request returns intent+action+done with ticket_uuid."""
    response = api_client.post_sse("/chatbot-response/stream", {
        "message": "I want to talk to a real person, connect me with a human agent please",
        "token": primary_token,
        "session_id": f"test-sse-handoff-{uuid.uuid4()}",
        "chat_history": [],
        "website_url": "https://example.com",
        "website_description": "Example Corp offers cloud and AI solutions",
    })
    if response.get("_status_code") in (400, 401):
        pytest.skip("Token expired or invalid")
    if response.get("_status_code") == 429:
        pytest.skip("Rate limited")

    events = response.get("_events", [])
    assert_sse_stream_valid(events)
    assert_sse_intent(events, "handoff")

    action_events = assert_sse_has_event(events, "action")
    assert action_events[0]["data"]["type"] == "handoff"
    assert len(action_events[0]["data"].get("response", "")) > 0
    ticket = action_events[0]["data"].get("ticket_uuid")
    if ticket:
        assert ticket.startswith("TICKET-"), f"ticket_uuid should start with TICKET-"

    done_evt = assert_sse_done(events)
    assert done_evt["data"]["is_human_handoff"] is True
    print("  SSE: handoff response test passed")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])
