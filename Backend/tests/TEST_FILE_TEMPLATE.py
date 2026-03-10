"""
🧪 [Test Suite Name] - [Platform] Simulator
[Description of what this test suite covers]

Usage:
    1. Copy this file to tests/usecases/[platform]/test_[feature].py
    2. Create corresponding [feature].cases.json in the same folder
    3. Update the test_cases_path to match your JSON file
    4. Implement custom assertion functions as needed
    5. Run: pytest tests/usecases/[platform]/test_[feature].py -v

Example:
    pytest tests/usecases/ionq/test_my_feature.py -v -s
    pytest -m ionq -v  # Run all IonQ tests
    pytest -m simulator -v  # Run all simulator tests
"""

import pytest
import json
from pathlib import Path
from helpers.api_client import APIClient
from helpers.assertions import (
    assert_quantum_results,
    assert_execution_time,
    assert_no_cost,
    assert_bell_state,  # For entanglement tests
)


# =============================================================================
# Load Test Cases from JSON
# =============================================================================
# TODO: Update this path to match your test file name
test_cases_path = Path(__file__).parent / "your_feature.cases.json"
with open(test_cases_path) as f:
    test_data = json.load(f)


# =============================================================================
# Custom Assertion Functions (Optional)
# =============================================================================
# Add custom assertions specific to your test suite here

def assert_custom_state(measurements: dict, expected_states: list, tolerance: float = 0.1):
    """
    Example custom assertion for specific quantum states
    
    Args:
        measurements: Dictionary of measurement counts {state: count}
        expected_states: List of expected basis states
        tolerance: Allowed deviation from expected probabilities
    """
    total = sum(measurements.values())
    
    # Check only expected states are present
    for state, count in measurements.items():
        if count > 0:
            assert state in expected_states, \
                f"Unexpected state |{state}⟩ found. Expected one of: {expected_states}"
    
    # Add more custom validations as needed
    print(f"✓ Custom state validation passed")


def assert_deterministic_result(measurements: dict, expected_state: str):
    """
    Assert that only one specific state is measured (deterministic circuit)
    
    Args:
        measurements: Dictionary of measurement counts
        expected_state: The single expected basis state (e.g., "111")
    """
    for state, count in measurements.items():
        if count > 0:
            assert state == expected_state, \
                f"Expected only |{expected_state}⟩, but found |{state}⟩"
    print(f"✓ Deterministic state |{expected_state}⟩ confirmed")


# =============================================================================
# Parametrized Tests (from JSON)
# =============================================================================

# TODO: Update markers to match your platform (ionq, quera, etc.)
@pytest.mark.ionq  # or @pytest.mark.quera
@pytest.mark.simulator
@pytest.mark.your_feature  # TODO: Add custom marker for this feature
@pytest.mark.parametrize("test_case", [tc for tc in test_data["tests"] if not tc.get("skip")])
def test_parametrized_cases(api_client: APIClient, test_case: dict):
    """
    Parametrized test that runs all cases from JSON file
    
    Each test case from the JSON file will be run as a separate test.
    The test_case dict contains 'name', 'description', 'input', 'expected', etc.
    """
    # Skip if marked
    if test_case.get("skip"):
        pytest.skip(test_case.get("skip_reason", "Test skipped"))
    
    # Mark as slow if tagged
    if "slow" in test_case.get("tags", []):
        pytest.mark.slow
    
    # Log test info
    print(f"\n🧪 Running: {test_case['name']}")
    print(f"📝 Description: {test_case['description']}")
    print(f"🎯 Shots: {test_case['input'].get('shots', 'N/A')}")
    
    # =========================================================================
    # Make API Request
    # =========================================================================
    # TODO: Update endpoint to match your API
    endpoint = "/ionq/submit-circuit"  # or "/quera/submit-ahs"
    response = api_client.post(endpoint, test_case["input"])
    
    # =========================================================================
    # Basic Assertions (always run)
    # =========================================================================
    # Assert basic quantum results (status code, simulation mode, etc.)
    assert_quantum_results(response, test_case["expected"])
    
    # Assert no cost for simulator mode
    if test_case["expected"].get("simulation_mode", True):
        assert_no_cost(response)
    
    # Assert execution time if specified
    if "max_execution_time" in test_case["expected"]:
        assert_execution_time(response, test_case["expected"]["max_execution_time"])
    
    # =========================================================================
    # Custom Assertions (based on test case type)
    # =========================================================================
    assertions = test_case.get("assertions", {})
    assertion_type = assertions.get("type")
    
    if assertion_type == "bell_state":
        measurements = response.get("measurement_counts", {})
        tolerance = assertions.get("tolerance", 0.1)
        assert_bell_state(measurements, tolerance=tolerance)
        print("✓ Bell state entanglement confirmed!")
        
    elif assertion_type == "deterministic":
        measurements = response.get("measurement_counts", {})
        expected_state = assertions.get("expected_state")
        if expected_state:
            assert_deterministic_result(measurements, expected_state)
            
    elif assertion_type == "custom":
        # TODO: Add your custom assertion logic here
        measurements = response.get("measurement_counts", {})
        expected_states = test_case["expected"].get("expected_states", [])
        if expected_states:
            assert_custom_state(measurements, expected_states)
    
    # =========================================================================
    # Print Results
    # =========================================================================
    if "measurement_counts" in response:
        measurements = response["measurement_counts"]
        print(f"\n📊 Measurement Results:")
        total = sum(measurements.values())
        for state, count in sorted(measurements.items()):
            prob = count / total if total > 0 else 0
            print(f"  |{state}⟩: {count} ({prob*100:.1f}%)")
    
    print(f"✅ Test passed: {test_case['name']}")


# =============================================================================
# Standalone Tests (not from JSON)
# =============================================================================

@pytest.mark.ionq  # TODO: Update marker
@pytest.mark.simulator
def test_basic_functionality(api_client: APIClient):
    """
    Basic smoke test to verify the API is working
    
    This test doesn't use the JSON file - it's a simple standalone test.
    """
    # TODO: Update with your basic test
    response = api_client.post("/ionq/submit-circuit", {
        "code": "circuit = Circuit().h(0)",
        "shots": 100,
        "use_simulator": True
    })
    
    assert response.get("_status_code") == 200, "Should return 200 status"
    assert response.get("status") == "COMPLETED", "Should complete immediately"
    assert response.get("simulation_mode") is True, "Should be in simulation mode"
    
    print("✓ Basic functionality test passed")


@pytest.mark.ionq  # TODO: Update marker
@pytest.mark.simulator
def test_response_metadata(api_client: APIClient):
    """
    Test that response includes all expected metadata fields
    """
    response = api_client.post("/ionq/submit-circuit", {
        "code": "circuit = Circuit().h(0).cnot(0, 1)",
        "shots": 100,
        "use_simulator": True
    })
    
    # Check response structure
    assert "_status_code" in response
    assert response["_status_code"] == 200
    
    # Check required metadata fields
    required_fields = ["status", "simulation_mode", "device_arn"]
    for field in required_fields:
        assert field in response, f"Response should include '{field}'"
    
    # Check optional but expected fields
    optional_fields = ["measurement_counts", "submission_time_seconds"]
    for field in optional_fields:
        if field in response:
            print(f"✓ Optional field '{field}' present")
    
    print("✓ All metadata fields verified")


@pytest.mark.ionq  # TODO: Update marker
@pytest.mark.simulator
def test_immediate_completion(api_client: APIClient):
    """
    Test that simulator completes immediately (no polling needed)
    """
    response = api_client.post("/ionq/submit-circuit", {
        "code": "circuit = Circuit().h(0)",
        "shots": 1000,
        "use_simulator": True
    })
    
    # Should complete immediately
    assert response["status"] == "COMPLETED", "Simulator should complete immediately"
    assert response["simulation_mode"] is True
    
    # Should have execution time
    assert "submission_time_seconds" in response
    exec_time = response["submission_time_seconds"]
    
    print(f"✓ Simulator completed in {exec_time*1000:.1f}ms")
    
    # Should be fast (< 1 second for simulator)
    assert exec_time < 1.0, f"Simulator took {exec_time}s, expected < 1.0s"


# =============================================================================
# Fixtures (Optional - can also be defined in conftest.py)
# =============================================================================

@pytest.fixture
def sample_input():
    """
    Fixture providing sample input data for tests
    Can be overridden in individual tests
    """
    return {
        "code": "circuit = Circuit().h(0)",
        "shots": 100,
        "use_simulator": True
    }


# =============================================================================
# Run Tests Directly
# =============================================================================

if __name__ == "__main__":
    # Run this specific test file with verbose output
    pytest.main([__file__, "-v", "-s"])

