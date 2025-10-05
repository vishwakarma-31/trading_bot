"""
Test Runner for the GoQuant Trading Bot
Runs all tests in the proper sequence to validate the complete system
"""
import sys
import os
import subprocess
import time

# Add src to path to import modules
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

def run_test_script(script_path: str, description: str) -> bool:
    """Run a test script and return success status"""
    print(f"\n{'='*60}")
    print(f"Running {description}")
    print(f"{'='*60}")
    
    try:
        # Run the test script
        result = subprocess.run([
            sys.executable, 
            script_path
        ], cwd=os.path.dirname(script_path), capture_output=True, text=True, timeout=120)
        
        # Print output
        if result.stdout:
            print(result.stdout)
        if result.stderr:
            print("STDERR:", result.stderr)
            
        return result.returncode == 0
        
    except subprocess.TimeoutExpired:
        print(f"❌ {description} timed out")
        return False
    except Exception as e:
        print(f"❌ {description} failed with exception: {e}")
        return False

def run_module_tests() -> dict:
    """Run individual module tests"""
    print("GoQuant Trading Bot - Complete System Test")
    print("=" * 60)
    
    # Define test scripts in order of dependency
    test_scripts = [
        # Basic module tests
        ("src/config/test_user_config_manager.py", "Configuration Management Tests"),
        ("src/utils/test_error_handling.py", "Error Handling Tests"),
        ("src/data_acquisition/test_data_acquisition.py", "Data Acquisition Tests"),
        ("src/data_processing/test_arbitrage_detector.py", "Arbitrage Detection Tests"),
        ("src/data_processing/test_market_view.py", "Market View Tests"),
        ("src/data_processing/test_service_controller.py", "Service Controller Tests"),
        ("src/telegram_bot/test_alert_manager.py", "Alert Manager Tests"),
        
        # Integration tests
        ("src/system/test_validation_scenarios.py", "Validation Scenarios Tests"),
        ("src/system/test_system_integration.py", "System Integration Tests")
    ]
    
    results = {}
    passed = 0
    total = len(test_scripts)
    
    # Run each test script
    for script_path, description in test_scripts:
        full_path = os.path.join(os.path.dirname(__file__), '..', script_path)
        if os.path.exists(full_path):
            success = run_test_script(full_path, description)
            results[description] = success
            if success:
                passed += 1
            print(f"\n{'✅' if success else '❌'} {description} {'PASSED' if success else 'FAILED'}")
        else:
            print(f"\n⚠️  {description} - Script not found: {script_path}")
            results[description] = False
    
    return results

def print_summary(results: dict):
    """Print test results summary"""
    print("\n" + "=" * 60)
    print("TEST RESULTS SUMMARY")
    print("=" * 60)
    
    passed = sum(1 for success in results.values() if success)
    total = len(results)
    
    for test_name, success in results.items():
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status} {test_name}")
    
    print("\n" + "=" * 60)
    print(f"FINAL RESULTS: {passed}/{total} test suites passed")
    
    success_rate = (passed / total) * 100 if total > 0 else 0
    print(f"SUCCESS RATE: {success_rate:.1f}%")
    
    if passed == total:
        print("\n🎉 ALL TESTS PASSED! The system is ready for deployment.")
        return True
    else:
        print(f"\n⚠️  {total - passed} test suite(s) failed. Please review the results above.")
        return False

def main():
    """Main test runner function"""
    print("GoQuant Trading Bot - Automated Test Runner")
    print("Starting comprehensive system validation...")
    
    start_time = time.time()
    
    # Run all tests
    results = run_module_tests()
    
    # Print summary
    success = print_summary(results)
    
    end_time = time.time()
    duration = end_time - start_time
    
    print(f"\nTotal test duration: {duration:.2f} seconds")
    
    return 0 if success else 1

if __name__ == "__main__":
    sys.exit(main())