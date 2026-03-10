"""
Test Configuration
Centralized configuration for AI Customer Support Widget tests
"""

import os
from pathlib import Path

try:
    from dotenv import load_dotenv
    env_path = Path(__file__).parent.parent.parent / '.env'
    if env_path.exists():
        load_dotenv(env_path)
except Exception:
    pass

API_BASE_URL = os.getenv('API_BASE_URL', 'http://localhost:8000')
API_TIMEOUT = int(os.getenv('API_TIMEOUT', '30'))

TEST_MODE = os.getenv('TEST_MODE', 'local')
RUN_SLOW_TESTS = os.getenv('RUN_SLOW_TESTS', 'true').lower() == 'true'
RUN_EXTERNAL_TESTS = os.getenv('RUN_EXTERNAL_TESTS', 'false').lower() == 'true'

LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')
LOG_FILE = os.getenv('LOG_FILE', 'tests/logs/test.log')

TEST_DATA_DIR = os.path.join(os.path.dirname(__file__), '..', 'usecases')

TEST_WEBSITE_URL = "https://example.com"
TEST_WEBSITE_DESCRIPTION = "Example company for testing purposes"


class TestConfig:

    def __init__(self):
        self.api_base_url = API_BASE_URL
        self.api_timeout = API_TIMEOUT
        self.test_mode = TEST_MODE
        self.run_slow_tests = RUN_SLOW_TESTS
        self.run_external_tests = RUN_EXTERNAL_TESTS
        self.log_level = LOG_LEVEL
        self.test_website_url = TEST_WEBSITE_URL
        self.test_website_description = TEST_WEBSITE_DESCRIPTION

    def is_local(self) -> bool:
        return self.test_mode == 'local'

    def is_staging(self) -> bool:
        return self.test_mode == 'staging'

    def is_production(self) -> bool:
        return self.test_mode == 'production'

    def should_skip_slow(self) -> bool:
        return not self.run_slow_tests

    def should_skip_external(self) -> bool:
        return not self.run_external_tests


config = TestConfig()
