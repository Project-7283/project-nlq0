#!/usr/bin/env python3
"""
Test runner for NLQ Enhancement project

Runs unit tests and integration tests with proper reporting.
"""

import sys
import os
import unittest

# Add project root to path
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))


def run_unit_tests():
    """Run unit tests"""
    print("\n" + "="*80)
    print("RUNNING UNIT TESTS")
    print("="*80 + "\n")
    
    loader = unittest.TestLoader()
    suite = loader.discover('tests/unit', pattern='test_*.py')
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    return result.wasSuccessful()


def run_integration_tests():
    """Run integration tests"""
    print("\n" + "="*80)
    print("RUNNING INTEGRATION TESTS")
    print("="*80 + "\n")
    
    loader = unittest.TestLoader()
    suite = loader.discover('tests/integration', pattern='test_*.py')
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    return result.wasSuccessful()


def run_specific_test(test_path):
    """Run a specific test file or test case"""
    print(f"\n{'='*80}")
    print(f"RUNNING: {test_path}")
    print("="*80 + "\n")
    
    loader = unittest.TestLoader()
    suite = loader.loadTestsFromName(test_path)
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    return result.wasSuccessful()


def main():
    """Main test runner"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Run tests for NLQ Enhancement')
    parser.add_argument(
        '--unit',
        action='store_true',
        help='Run only unit tests'
    )
    parser.add_argument(
        '--integration',
        action='store_true',
        help='Run only integration tests'
    )
    parser.add_argument(
        '--test',
        type=str,
        help='Run specific test (e.g., tests.unit.test_data_governance.TestDataGovernanceService)'
    )
    parser.add_argument(
        '--coverage',
        action='store_true',
        help='Run tests with coverage report'
    )
    
    args = parser.parse_args()
    
    # Setup environment for tests
    os.environ["DATA_GOVERNANCE_ENABLED"] = "true"
    os.environ["DATA_GOVERNANCE_STRICT_MODE"] = "true"
    
    success = True
    
    if args.test:
        # Run specific test
        success = run_specific_test(args.test)
    elif args.unit:
        # Run only unit tests
        success = run_unit_tests()
    elif args.integration:
        # Run only integration tests
        success = run_integration_tests()
    else:
        # Run all tests
        unit_success = run_unit_tests()
        integration_success = run_integration_tests()
        success = unit_success and integration_success
    
    # Print summary
    print("\n" + "="*80)
    if success:
        print("✅ ALL TESTS PASSED")
    else:
        print("❌ SOME TESTS FAILED")
    print("="*80 + "\n")
    
    sys.exit(0 if success else 1)


if __name__ == '__main__':
    main()
