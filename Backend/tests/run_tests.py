#!/usr/bin/env python3
"""
Test Runner for AI Customer Support Widget API

Usage:
    python tests/run_tests.py                   # Run all tests
    python tests/run_tests.py chatbot           # Run chatbot tests only
    python tests/run_tests.py auth              # Run auth tests only
    python tests/run_tests.py --verbose         # Verbose output
    python tests/run_tests.py --fail-fast       # Stop on first failure
    python tests/run_tests.py --markers         # List all markers
    python tests/run_tests.py --token "eyJ..."  # Set JWT token for all users
"""

import sys
import os
import argparse
from pathlib import Path
import pytest
import json
from datetime import datetime, timezone

project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))


def print_banner():
    print("""
========================================================================
         AI Customer Support Widget — API Test Suite
                    Powered by pytest
========================================================================
""")


def use_provided_token(config_file: Path, token: str, user_type: str = 'all') -> bool:
    if not token or len(token) < 20:
        print("  Invalid token format")
        return False

    if not config_file.exists():
        print(f"  Config file not found: {config_file}")
        return False

    with open(config_file, 'r') as f:
        config = json.load(f)

    backup_file = config_file.with_suffix('.json.backup')
    with open(backup_file, 'w') as f:
        json.dump(config, f, indent=2)

    if user_type == 'all':
        for user_key in config['users'].keys():
            config['users'][user_key]['token'] = token
            print(f"  Updated {user_key} user token")
    elif user_type in config['users']:
        config['users'][user_type]['token'] = token
        print(f"  Updated {user_type} user token")
    else:
        print(f"  Unknown user type: {user_type}")
        return False

    config['lastUpdated'] = datetime.now(timezone.utc).isoformat()
    config['setupComplete'] = True
    with open(config_file, 'w') as f:
        json.dump(config, f, indent=2)

    print(f"  Token set successfully (backup: {backup_file.name})")
    return True


def list_markers():
    print("\nAvailable Test Markers:")
    markers = {
        "health": "Root / health-check endpoint tests",
        "auth": "Authentication and token verification tests",
        "chatbot": "Chatbot response and chat history tests",
        "ticket": "Support ticket CRUD tests",
        "stats": "Conversation statistics tests",
        "ingestion": "Data scraping, embedding and search tests",
        "slow": "Slow-running tests (>5 seconds)",
        "smoke": "Quick smoke tests for CI/CD",
        "integration": "Full integration tests",
        "external": "Tests requiring external services (Gemini, Pinecone, etc.)",
    }
    for marker, description in markers.items():
        print(f"  {marker:15} - {description}")

    print("\nUsage:")
    print('  pytest -m chatbot              # Run only chatbot tests')
    print('  pytest -m auth                 # Run only auth tests')
    print('  pytest -m "not external"       # Skip external service tests')
    print('  pytest -m "not slow"           # Skip slow tests')


def main():
    parser = argparse.ArgumentParser(
        description="AI Customer Support Widget API Test Suite",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python tests/run_tests.py                     # Run all tests
  python tests/run_tests.py --token "eyJ..."    # Set token, then run
  python tests/run_tests.py chatbot             # Run chatbot tests only
  python tests/run_tests.py auth --verbose      # Verbose auth tests
  python tests/run_tests.py --fail-fast         # Stop on first failure
        """
    )
    parser.add_argument('pattern', nargs='?', default=None,
                        help='Test pattern or marker (e.g., chatbot, auth, ticket)')
    parser.add_argument('-v', '--verbose', action='store_true')
    parser.add_argument('-x', '--fail-fast', action='store_true')
    parser.add_argument('-s', '--capture', action='store_true', help='Show print statements')
    parser.add_argument('-m', '--markers', action='store_true', help='List markers')
    parser.add_argument('--token', type=str, help='JWT token to use for all test users')
    parser.add_argument('--token-user', choices=['primary', 'secondary', 'all'],
                        default='all', help='Which user to update with token (default: all)')

    args = parser.parse_args()
    print_banner()

    if args.markers:
        list_markers()
        return 0

    config_file = Path(__file__).parent / 'config' / 'persistent-users.json'

    if args.token:
        success = use_provided_token(config_file, args.token, args.token_user)
        if not success:
            print("\n  Failed to set provided token\n")
            return 1

    pytest_args = ['tests/usecases']

    if args.verbose:
        pytest_args.append('-v')
    else:
        pytest_args.append('-q')

    if args.fail_fast:
        pytest_args.append('-x')

    if args.capture:
        pytest_args.append('-s')

    if args.pattern:
        pytest_args.extend(['-k', args.pattern])
        print(f"  Running tests matching: {args.pattern}")
    else:
        print("  Running all tests")

    print(f"  pytest command: pytest {' '.join(pytest_args)}\n")

    exit_code = pytest.main(pytest_args)

    if exit_code == 0:
        print("\n  All tests passed!")
    else:
        print("\n  Some tests failed")

    return exit_code


if __name__ == "__main__":
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        print("\n  Test execution interrupted")
        sys.exit(1)
    except Exception as e:
        print(f"\n  Fatal error: {e}")
        sys.exit(1)
