"""
Authentication Helper for AI Customer Support Widget Tests
Provides utilities for JWT token management and authenticated requests
"""
import json
import os
import httpx
from typing import Dict, Optional
from pathlib import Path

PERSISTENT_USERS_FILE = Path(__file__).parent.parent / "config" / "persistent-users.json"


def load_persistent_users() -> Dict:
    if not PERSISTENT_USERS_FILE.exists():
        raise FileNotFoundError(f"Persistent users file not found: {PERSISTENT_USERS_FILE}")
    with open(PERSISTENT_USERS_FILE, 'r') as f:
        return json.load(f)


def get_test_user(user_type: str = "primary") -> Dict:
    users_config = load_persistent_users()
    if user_type not in users_config["users"]:
        raise ValueError(f"Unknown user type: {user_type}. Available: {list(users_config['users'].keys())}")
    return users_config["users"][user_type]


def get_auth_headers(token: str) -> Dict[str, str]:
    return {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }


def get_auth_token_for_tests(user_type: str = "primary") -> str:
    user = get_test_user(user_type)
    token = user.get("token", "")
    if not token:
        raise ValueError(
            f"No token set for user '{user_type}'. "
            f"Authenticate via /google-login and paste the token into persistent-users.json"
        )
    return token


class AuthenticatedClient:
    """HTTP client with automatic JWT authentication for chatbot widget API."""

    def __init__(self, token: str, base_url: str = "http://localhost:8000"):
        self.token = token
        self.base_url = base_url
        self.headers = get_auth_headers(token)

    async def post(self, endpoint: str, json_data: Dict = None, **kwargs) -> httpx.Response:
        """Make authenticated POST request. Token is sent via Authorization header."""
        async with httpx.AsyncClient(verify=False, timeout=30.0) as client:
            url = f"{self.base_url}{endpoint}"
            return await client.post(url, json=json_data, headers=self.headers, **kwargs)

    async def get(self, endpoint: str, **kwargs) -> httpx.Response:
        async with httpx.AsyncClient(verify=False, timeout=30.0) as client:
            url = f"{self.base_url}{endpoint}"
            return await client.get(url, headers=self.headers, **kwargs)

    async def put(self, endpoint: str, json_data: Dict = None, **kwargs) -> httpx.Response:
        async with httpx.AsyncClient(verify=False, timeout=30.0) as client:
            url = f"{self.base_url}{endpoint}"
            return await client.put(url, json=json_data, headers=self.headers, **kwargs)


def get_primary_user_token() -> str:
    return get_auth_token_for_tests("primary")


def get_secondary_user_token() -> str:
    return get_auth_token_for_tests("secondary")


def get_api_url() -> str:
    return os.getenv("API_BASE_URL") or "http://localhost:8000"
