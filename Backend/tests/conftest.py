"""
Pytest Configuration and Fixtures
Shared fixtures for AI Customer Support Widget tests
"""

import pytest
import sys
import os
import logging
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from tests.helpers.api_client import APIClient
from tests.config.test_config import config
from tests.helpers.auth_helper import (
    get_test_user,
    get_auth_token_for_tests,
    AuthenticatedClient,
    get_primary_user_token,
    get_secondary_user_token,
    get_api_url,
    load_persistent_users,
)

logger = logging.getLogger(__name__)


# ============================================================================
# AUTHENTICATION FIXTURES
# ============================================================================

@pytest.fixture(scope="session")
def primary_user():
    return get_test_user("primary")


@pytest.fixture(scope="session")
def secondary_user():
    return get_test_user("secondary")


@pytest.fixture(scope="session")
def primary_token():
    try:
        return get_primary_user_token()
    except ValueError:
        pytest.skip("No primary user token configured in persistent-users.json")


@pytest.fixture(scope="session")
def secondary_token():
    try:
        return get_secondary_user_token()
    except ValueError:
        pytest.skip("No secondary user token configured in persistent-users.json")


@pytest.fixture(scope="session")
def auth_client(primary_token):
    return AuthenticatedClient(
        token=primary_token,
        base_url=get_api_url()
    )


@pytest.fixture(scope="function")
def fresh_auth_client(primary_token):
    return AuthenticatedClient(
        token=primary_token,
        base_url=get_api_url()
    )


# ============================================================================
# API CLIENT FIXTURES
# ============================================================================

@pytest.fixture(scope="session")
def api_client(primary_token):
    client = APIClient(base_url=config.api_base_url, timeout=config.api_timeout)
    client.set_auth_token(primary_token)
    yield client
    client.close()


@pytest.fixture(scope="function")
def fresh_api_client(primary_token):
    client = APIClient(base_url=config.api_base_url, timeout=config.api_timeout)
    client.set_auth_token(primary_token)
    yield client
    client.close()


@pytest.fixture(scope="session")
def unauthenticated_client():
    """API client without any auth token."""
    client = APIClient(base_url=config.api_base_url, timeout=config.api_timeout)
    yield client
    client.close()


# ============================================================================
# CONFIG FIXTURES
# ============================================================================

@pytest.fixture(scope="session")
def test_config():
    return config


@pytest.fixture
def test_website():
    """Default website config for chatbot tests."""
    return {
        "website_url": config.test_website_url,
        "website_description": config.test_website_description,
    }


# ============================================================================
# AUTO-SKIP FIXTURES
# ============================================================================

@pytest.fixture(autouse=True)
def skip_slow_tests(request):
    if request.node.get_closest_marker('slow'):
        if config.should_skip_slow():
            pytest.skip('Slow tests disabled (set RUN_SLOW_TESTS=true to enable)')


@pytest.fixture(autouse=True)
def skip_external_tests(request):
    if request.node.get_closest_marker('external'):
        if config.should_skip_external():
            pytest.skip('External service tests disabled (set RUN_EXTERNAL_TESTS=true to enable)')


# ============================================================================
# PYTEST HOOKS
# ============================================================================

def pytest_configure(config):
    from tests.config.test_config import config as test_config

    log_dir = Path(__file__).parent / 'logs'
    log_dir.mkdir(exist_ok=True)

    try:
        users_config = load_persistent_users()
        primary_user = users_config["users"]["primary"]
        has_token = bool(primary_user.get("token"))
        auth_status = f"Token present: {has_token} (email: {primary_user['email']})"
    except Exception as e:
        auth_status = f"Failed to load: {e}"

    print("\n" + "=" * 80)
    print("AI Customer Support Widget — Test Configuration")
    print(f"  API Base URL: {test_config.api_base_url}")
    print(f"  Test Mode: {test_config.test_mode}")
    print(f"  Run Slow Tests: {test_config.run_slow_tests}")
    print(f"  Run External Tests: {test_config.run_external_tests}")
    print(f"  Authentication: {auth_status}")
    print("=" * 80 + "\n")


def pytest_collection_modifyitems(config, items):
    for item in items:
        path_str = str(item.fspath)
        if 'chatbot' in path_str:
            item.add_marker(pytest.mark.chatbot)
        if 'auth' in path_str:
            item.add_marker(pytest.mark.auth)
        if 'ticket' in path_str:
            item.add_marker(pytest.mark.ticket)
        if 'stats' in path_str:
            item.add_marker(pytest.mark.stats)
        if 'ingestion' in path_str:
            item.add_marker(pytest.mark.ingestion)
        if 'health' in path_str:
            item.add_marker(pytest.mark.health)


def pytest_runtest_makereport(item, call):
    if call.when == "call":
        duration = call.stop - call.start
        if duration > 5.0:
            print(f"\n  Slow test: {item.nodeid} took {duration:.2f}s")
