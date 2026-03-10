"""
Custom Assertion Helpers for AI Customer Support Widget Testing
Provides API-specific assertions and validation
"""

from typing import Dict, Any, List


def assert_status_code(response: Dict[str, Any], expected: int, message: str = ""):
    actual = response.get('_status_code', response.get('status_code'))
    assert actual == expected, f"{message} Expected status {expected}, got {actual}"


def assert_field_equals(response: Dict[str, Any], field: str, expected: Any, message: str = ""):
    actual = response.get(field)
    assert actual == expected, f"{message} Field '{field}': expected {expected}, got {actual}"


def assert_field_exists(response: Dict[str, Any], field: str, message: str = ""):
    assert field in response, f"{message} Field '{field}' not found in response"


def assert_field_type(response: Dict[str, Any], field: str, expected_type: type, message: str = ""):
    assert field in response, f"{message} Field '{field}' not found"
    actual = response[field]
    assert isinstance(actual, expected_type), \
        f"{message} Field '{field}': expected type {expected_type.__name__}, got {type(actual).__name__}"


def assert_all_fields_present(response: Dict[str, Any], required_fields: List[str]):
    missing = [f for f in required_fields if f not in response]
    assert not missing, f"Missing required fields: {', '.join(missing)}"


def assert_response_structure(response: Dict[str, Any], expected_structure: Dict[str, type]):
    for field, expected_type in expected_structure.items():
        assert field in response, f"Field '{field}' not found in response"
        actual_value = response[field]
        assert isinstance(actual_value, expected_type), \
            f"Field '{field}': expected type {expected_type.__name__}, got {type(actual_value).__name__}"


def assert_contains(response: Dict[str, Any], field: str, substring: str, message: str = ""):
    assert field in response, f"{message} Field '{field}' not found"
    actual = str(response[field])
    assert substring in actual, \
        f"{message} Field '{field}' does not contain '{substring}'. Actual: {actual}"


# ──────────────────────────────────────────────────────────────────────────────
# Chatbot-Specific Assertions
# ──────────────────────────────────────────────────────────────────────────────

def assert_chatbot_response(response: Dict[str, Any], message: str = ""):
    """Assert the response matches the ChatbotResponse schema."""
    assert_status_code(response, 200, message)
    assert_field_exists(response, "response", message)
    assert_field_exists(response, "is_booking", message)
    assert_field_exists(response, "is_human_handoff", message)
    assert_field_type(response, "response", str, message)
    assert_field_type(response, "is_booking", bool, message)
    assert_field_type(response, "is_human_handoff", bool, message)

    assert not (response["is_booking"] and response["is_human_handoff"]), \
        f"{message} is_booking and is_human_handoff cannot both be true"


def assert_booking_response(response: Dict[str, Any], message: str = ""):
    """Assert a booking-intent chatbot response."""
    assert_chatbot_response(response, message)
    assert response["is_booking"] is True, f"{message} Expected is_booking=true"
    assert response["is_human_handoff"] is False, f"{message} Expected is_human_handoff=false"


def assert_handoff_response(response: Dict[str, Any], message: str = ""):
    """Assert a human-handoff chatbot response."""
    assert_chatbot_response(response, message)
    assert response["is_human_handoff"] is True, f"{message} Expected is_human_handoff=true"
    assert response["is_booking"] is False, f"{message} Expected is_booking=false"
    if "ticket_uuid" in response and response["ticket_uuid"] is not None:
        assert response["ticket_uuid"].startswith("TICKET-"), \
            f"{message} ticket_uuid should start with 'TICKET-'"


def assert_regular_response(response: Dict[str, Any], message: str = ""):
    """Assert a regular (non-booking, non-handoff) chatbot response."""
    assert_chatbot_response(response, message)
    assert response["is_booking"] is False, f"{message} Expected is_booking=false"
    assert response["is_human_handoff"] is False, f"{message} Expected is_human_handoff=false"


# ──────────────────────────────────────────────────────────────────────────────
# Auth Assertions
# ──────────────────────────────────────────────────────────────────────────────

def assert_auth_success(response: Dict[str, Any], message: str = ""):
    """Assert a successful authentication response."""
    assert_status_code(response, 200, message)
    assert_field_equals(response, "status", True, message)
    assert_field_exists(response, "result", message)
    result = response["result"]
    assert "token" in result, f"{message} Token missing from auth result"


def assert_auth_failure(response: Dict[str, Any], message: str = ""):
    """Assert that authentication was rejected."""
    actual = response.get('_status_code')
    assert actual in (400, 401, 403, 500), \
        f"{message} Expected auth failure status (400/401/403/500), got {actual}"


def assert_token_verified(response: Dict[str, Any], message: str = ""):
    """Assert a successful token verification response."""
    assert_status_code(response, 200, message)
    assert_field_equals(response, "status", True, message)
    assert_field_exists(response, "user", message)


# ──────────────────────────────────────────────────────────────────────────────
# Ticket Assertions
# ──────────────────────────────────────────────────────────────────────────────

def assert_ticket_structure(ticket: Dict[str, Any], message: str = ""):
    """Assert a ticket object has the expected fields."""
    expected_fields = ["id", "uuid", "user_id", "session_id", "message", "status"]
    for field in expected_fields:
        assert field in ticket, f"{message} Ticket missing field '{field}'"


def assert_ticket_status(ticket: Dict[str, Any], expected_status: str, message: str = ""):
    """Assert a ticket has a specific status."""
    assert ticket.get("status") == expected_status, \
        f"{message} Expected ticket status '{expected_status}', got '{ticket.get('status')}'"


# ──────────────────────────────────────────────────────────────────────────────
# Stats Assertions
# ──────────────────────────────────────────────────────────────────────────────

def assert_stats_structure(response: Dict[str, Any], message: str = ""):
    """Assert a stats response has the expected numeric fields."""
    numeric_fields = [
        "conversations", "messages", "bookings", "human_handoffs",
        "successful_conversations", "success_rate", "avg_messages_per_conversation"
    ]
    for field in numeric_fields:
        assert field in response, f"{message} Stats missing field '{field}'"
        val = response[field]
        assert isinstance(val, (int, float)), \
            f"{message} Stats field '{field}' should be numeric, got {type(val).__name__}"


# ──────────────────────────────────────────────────────────────────────────────
# Generic Error Assertions
# ──────────────────────────────────────────────────────────────────────────────

def assert_validation_error(response: Dict[str, Any], message: str = ""):
    """Assert a 422 Unprocessable Entity response (Pydantic validation failure)."""
    assert_status_code(response, 422, message)
    assert "detail" in response, f"{message} Validation error should have 'detail' field"


def assert_not_found_or_error(response: Dict[str, Any], message: str = ""):
    """Assert a 4xx/5xx response."""
    actual = response.get('_status_code')
    assert actual >= 400, f"{message} Expected error status (>=400), got {actual}"


def assert_rate_limited(response: Dict[str, Any], message: str = ""):
    """Assert a 429 Too Many Requests response."""
    assert_status_code(response, 429, message)
