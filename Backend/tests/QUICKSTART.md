# Quick Start Guide - AI Customer Support Widget Tests

## Setup (5 minutes)

### 1. Install Test Dependencies

```bash
cd Backend
uv add --dev pytest pytest-asyncio httpx pyjwt
```

### 2. Start the API Server

```bash
cd Backend/app
uvicorn app:app --host 0.0.0.0 --port 8000 --reload
```

Wait for: `Application startup complete`

### 3. Configure Auth Tokens

Authenticate via the chatbot widget (Google OAuth), then copy the JWT from `localStorage` (`chatbotAuthToken` key) and paste it into `tests/config/persistent-users.json`:

```json
{
  "users": {
    "primary": {
      "token": "eyJhbGciOiJIUzI1NiI..."
    }
  }
}
```

Or use the runner:

```bash
python tests/run_tests.py --token "eyJhbGciOiJIUzI1NiI..."
```

### 4. Run Tests

```bash
python tests/run_tests.py
```

## Common Commands

### Run All Tests
```bash
python tests/run_tests.py
# or
pytest tests/usecases/
```

### Run Specific Module Tests
```bash
python tests/run_tests.py chatbot       # Chatbot tests only
python tests/run_tests.py auth          # Auth tests only
python tests/run_tests.py ticket        # Ticket tests only
python tests/run_tests.py stats         # Stats tests only
python tests/run_tests.py ingestion     # Ingestion tests only
python tests/run_tests.py health        # Health check tests only
```

### Run with Options
```bash
python tests/run_tests.py --verbose           # Detailed output
python tests/run_tests.py --fail-fast         # Stop on first failure
python tests/run_tests.py chatbot --verbose   # Chatbot with details
```

### Using pytest Directly
```bash
pytest tests/usecases/                        # All tests
pytest tests/usecases/chatbot/                # Chatbot directory
pytest tests/usecases/auth/test_auth.py       # Specific file
pytest -v                                     # Verbose
pytest -x                                     # Fail fast
pytest -s                                     # Show print statements
pytest -k "booking"                           # Tests matching "booking"
```

### Filter by Markers
```bash
pytest -m chatbot                             # Only chatbot tests
pytest -m auth                                # Only auth tests
pytest -m smoke                               # Quick smoke tests
pytest -m "not external"                      # Skip external service tests
pytest -m "not slow"                          # Skip slow tests
```

## Test Structure

```
tests/
├── usecases/
│   ├── health/            # Root endpoint tests
│   ├── auth/              # Google login & JWT tests
│   ├── chatbot/           # Chatbot response tests
│   ├── ticket/            # Support ticket CRUD tests
│   ├── stats/             # Conversation stats tests
│   └── ingestion/         # Scrape & vector search tests
├── helpers/               # API client, assertions, auth
├── config/                # Test config, persistent users
├── conftest.py            # pytest fixtures
├── pytest.ini             # pytest configuration
└── run_tests.py           # Main runner
```

## Writing a New Test

### 1. Create Test Cases (JSON)

`tests/usecases/mymodule/mymodule.cases.json`:
```json
{
  "suite": "My Test Suite",
  "description": "What this tests",
  "tests": [
    {
      "name": "my_test_case",
      "description": "Test description",
      "input": {
        "method": "POST",
        "endpoint": "/my-endpoint",
        "body": {"key": "value"}
      },
      "expected": {
        "status_code": 200
      },
      "skip": false
    }
  ]
}
```

### 2. Create Test File (Python)

`tests/usecases/mymodule/test_mymodule.py`:
```python
import pytest
import json
from pathlib import Path
from helpers.api_client import APIClient
from helpers.assertions import assert_status_code

test_cases_path = Path(__file__).parent / "mymodule.cases.json"
with open(test_cases_path) as f:
    test_data = json.load(f)

@pytest.mark.parametrize("test_case", test_data["tests"])
def test_my_endpoint(api_client, test_case):
    response = api_client.post(test_case["input"]["endpoint"], test_case["input"]["body"])
    assert_status_code(response, test_case["expected"]["status_code"])
```

### 3. Run Your Test

```bash
pytest tests/usecases/mymodule/ -v
```

## Common Issues

### "Connection refused"
Start the API server first: `uvicorn app:app --port 8000`

### "Token expired or invalid"
Re-authenticate via Google OAuth and update the token in `persistent-users.json`

### Tests timeout
Increase timeout: `pytest --timeout=120`

### External service tests failing
Skip them: `pytest -m "not external"`
