# AI Customer Support Widget — API Testing Framework

A pytest-based testing framework with JSON-driven test cases and module-based organization for the Embeddable AI Customer Support Widget backend.

## API Endpoints Covered

| Method | Endpoint | Module | Auth |
|--------|----------|--------|------|
| GET | `/` | health | None |
| GET | `/sentry-debug` | health | None |
| POST | `/google-login` | auth | None (Google credential in body) |
| GET | `/verify-token` | auth | Bearer header |
| POST | `/chatbot-response` | chatbot | JWT in body |
| GET | `/all-chats` | chatbot | JWT in body |
| POST | `/stats` | stats | JWT in body |
| GET | `/stats` | stats | JWT in body |
| PUT | `/ticket` | ticket | None |
| GET | `/ticket/{uuid}` | ticket | None |
| GET | `/tickets` | ticket | JWT in body |
| POST | `/ingestion/scrape-website` | ingestion | Bearer header |
| GET | `/ingestion/search` | ingestion | Bearer header |

## Quick Start

```bash
# 1. Start the backend
cd Backend/app && uvicorn app:app --port 8000 --reload

# 2. Set auth token
python tests/run_tests.py --token "YOUR_JWT_HERE"

# 3. Run all tests
python tests/run_tests.py
```

## Test Markers

| Marker | Description |
|--------|-------------|
| `health` | Root / health-check endpoint tests |
| `auth` | Authentication and token verification tests |
| `chatbot` | Chatbot response and chat history tests |
| `ticket` | Support ticket CRUD tests |
| `stats` | Conversation statistics tests |
| `ingestion` | Data scraping, embedding and search tests |
| `smoke` | Quick smoke tests for CI/CD |
| `slow` | Slow-running tests (>5 seconds) |
| `external` | Tests requiring external services (Gemini, Pinecone, etc.) |
| `integration` | Full integration tests |

## Test Types

Each test module contains two types of tests:

1. **Parametrized tests** — Driven by JSON case files. Each entry in the `tests` array becomes a separate pytest test case. Easy to add new scenarios without writing Python code.

2. **Standalone tests** — Written directly in Python for complex assertions, multi-step flows, or edge cases that don't fit the JSON format well.

## Available Assertion Helpers

```python
from helpers.assertions import (
    # Generic
    assert_status_code, assert_field_exists, assert_field_equals,
    assert_field_type, assert_all_fields_present, assert_contains,
    assert_validation_error, assert_not_found_or_error, assert_rate_limited,

    # Chatbot-specific
    assert_chatbot_response,     # Full ChatbotResponse schema check
    assert_booking_response,     # is_booking=true
    assert_handoff_response,     # is_human_handoff=true + ticket_uuid
    assert_regular_response,     # Both flags false

    # Auth-specific
    assert_auth_success, assert_auth_failure, assert_token_verified,

    # Ticket-specific
    assert_ticket_structure, assert_ticket_status,

    # Stats-specific
    assert_stats_structure,
)
```

## Configuration

### Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `API_BASE_URL` | `http://localhost:8000` | Backend API URL |
| `API_TIMEOUT` | `30` | Request timeout (seconds) |
| `TEST_MODE` | `local` | Test environment (local/staging/production) |
| `RUN_SLOW_TESTS` | `true` | Whether to run slow tests |
| `RUN_EXTERNAL_TESTS` | `false` | Whether to run tests hitting external services |

### Auth Token Setup

Tests that require authentication need valid JWT tokens in `config/persistent-users.json`. To obtain tokens:

1. Start the backend server
2. Open the frontend and authenticate via Google OAuth
3. Open browser DevTools > Application > Local Storage > `chatbotAuthToken`
4. Copy the token and either:
   - Paste into `persistent-users.json` under `users.primary.token`
   - Or run: `python tests/run_tests.py --token "YOUR_TOKEN"`

## Debugging

```bash
pytest tests/usecases/chatbot/test_chatbot.py::test_chatbot_returns_valid_response -v -s
pytest --pdb                    # Drop into debugger on failure
pytest --tb=long                # Full traceback
pytest -vv                      # Extra verbose
```
