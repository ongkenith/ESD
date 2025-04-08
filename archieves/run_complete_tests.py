#!/usr/bin/env python
import sys
import os
import subprocess
import time
from datetime import datetime

def print_header(title):
    """Print a formatted section header"""
    line = "=" * 80
    print("\n" + line)
    print(f"{title:^80}")
    print(line + "\n")

def run_command(command, shell=False):
    """Run a command and return the exit code"""
    print(f"Running command: {command}")
    process = subprocess.run(command, shell=shell, capture_output=False)
    return process.returncode

def determine_test_success(script_name, exit_code, output=None):
    """Determine if a test was actually successful based on output and script name"""
    # For now, we'll use exit code as the primary success indicator
    # This could be enhanced to parse output for specific failure patterns
    return exit_code == 0

def main():
    # Parse command line arguments
    docker_mode = '--docker' in sys.argv
    env_vars = os.environ.copy()
    
    if docker_mode:
        env_vars['DOCKER_MODE'] = 'true'
        print("Running tests in Docker mode")
    else:
        print("Running tests in local mode")

    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print_header(f"RUNNING COMPLETE SYSTEM TESTS - {timestamp}")
    
    # Define the test scripts to run
    test_scripts = [
        {
            "name": "Weather Check Service Test",
            "script": "test_weather_check.py",
            "args": []
        },
        {
            "name": "Notification Service API Test",
            "script": "test_notification_service.py",
            "args": ["--api-only"]
        },
        {
            "name": "Notification Service Queue Test",
            "script": "test_notification_service.py",
            "args": ["--queue-only"]
        },
        {
            "name": "Order Processing Test",
            "script": "test_process_order.py",
            "args": []
        },
        {
            "name": "Full End-to-End Order Flow Simulation",
            "script": "test_full_order_flow.py",
            "args": []
        }
    ]
    
    # Track test results
    results = []
    
    # Run each test script
    for i, test in enumerate(test_scripts, 1):
        print_header(f"TEST {i}/{len(test_scripts)}: {test['name']}")
        
        command = [sys.executable, test["script"]]
        if docker_mode:
            command.append("--docker")
        command.extend(test["args"])
        
        start_time = time.time()
        exit_code = run_command(command)
        end_time = time.time()
        
        duration = end_time - start_time
        
        # Determine if the test was truly successful
        success = determine_test_success(test["script"], exit_code)
        
        # Record the result
        results.append({
            "name": test["name"],
            "success": success,
            "duration": duration
        })
        
        print(f"\nTest execution completed with status: {'SUCCESS' if exit_code == 0 else 'FAILURE'}")
        print(f"Test actual result: {'PASSED' if success else 'FAILED'}")
        print(f"Duration: {duration:.2f} seconds\n")
        print("-" * 80)
    
    # Print summary
    print_header("TEST SUMMARY")
    
    pass_count = sum(1 for result in results if result["success"])
    fail_count = len(results) - pass_count
    
    for i, result in enumerate(results, 1):
        status = "✅ PASSED" if result["success"] else "❌ FAILED"
        print(f"{i}. {result['name']}: {status} ({result['duration']:.2f}s)")
    
    print("\n" + "-" * 80)
    print(f"TOTAL TESTS: {len(results)}")
    print(f"PASSED: {pass_count}")
    print(f"FAILED: {fail_count}")
    
    # Determine overall success
    if fail_count > 0:
        print("\n❌ SOME TESTS FAILED")
        return 1
    else:
        print("\n✅ ALL TESTS PASSED")
        return 0

if __name__ == "__main__":
    sys.exit(main()) 