#!/usr/bin/env python3
"""
Test Script for Image Processing Application

This script provides testing utilities and can be extended with actual tests.
Run with: uv run scripts/test.py
"""

import sys
import requests
import subprocess

from shared.config import settings


def check_backend_health():
    """Check if the backend is running and healthy"""

    try:
        backend_url = f"http://{settings.API_HOST}:{settings.API_PORT}/health"
        response = requests.get(backend_url, timeout=5)
        if response.status_code == 200:
            print("✅ Backend is healthy")
            return True
        else:
            print(f"❌ Backend health check failed: {response.status_code}")
            return False
    except requests.exceptions.RequestException as e:
        print(f"❌ Backend is not accessible: {e}")
        return False


def test_backend_units():
    """Check if the backend unit tests are passing"""

    try:
        result = subprocess.run(
            ["uv", "run", "pytest", "backend"], capture_output=True, text=True)
        if result.returncode == 0:
            print("✅ Backend unit tests passed")
            return True
        else:
            print(f"❌ Backend unit tests failed: {result.stderr}")
            return False
    except subprocess.CalledProcessError as e:
        print(f"❌ Backend unit tests error: {e}")
        return False


def check_frontend_accessibility():
    """Check if the frontend is accessible"""

    try:
        frontend_url = f"http://{settings.FRONTEND_HOST}:{settings.FRONTEND_PORT}"
        response = requests.get(frontend_url, timeout=5)
        if response.status_code == 200:
            print("✅ Frontend is accessible")
            return True
        else:
            print(
                f"❌ Frontend accessibility check failed: {response.status_code}")
            return False
    except requests.exceptions.RequestException as e:
        print(f"❌ Frontend is not accessible: {e}")
        return False


def test_frontend_units():
    """Check if the frontend unit tests are passing"""

    try:
        result = subprocess.run(
            ["uv", "run", "pytest", "frontend"], capture_output=True, text=True)
        if result.returncode == 0:
            print("✅ Frontend unit tests passed")
            return True
        else:
            print(f"❌ Frontend unit tests failed: {result.stderr}")
            return False
    except subprocess.CalledProcessError as e:
        print(f"❌ Frontend unit tests error: {e}")
        return False


def test_api_endpoints():
    """Test basic API endpoints"""
    print("\n🔍 Testing API endpoints...")

    base_url = f"http://{settings.API_HOST}:{settings.API_PORT}"

    # Test health endpoint
    try:
        response = requests.get(f"{base_url}/health")
        if response.status_code == 200:
            print("✅ Health endpoint working")
        else:
            print(f"❌ Health endpoint failed: {response.status_code}")
    except Exception as e:
        print(f"❌ Health endpoint error: {e}")

    # Test API docs
    try:
        response = requests.get(f"{base_url}/docs")
        if response.status_code == 200:
            print("✅ API documentation accessible")
        else:
            print(f"❌ API docs failed: {response.status_code}")
    except Exception as e:
        print(f"❌ API docs error: {e}")


def run_basic_tests():
    """Run basic application tests"""
    print("🧪 Running basic tests...")

    # Check if services are running
    backend_healthy = check_backend_health()
    frontend_accessible = check_frontend_accessibility()

    if backend_healthy:
        test_backend_units()

    if frontend_accessible:
        test_frontend_units()

    test_api_endpoints()

    print("\n📊 Test Summary:")
    print(f"Backend Health: {'✅ PASS' if backend_healthy else '❌ FAIL'}")
    print(f"Frontend Access: {'✅ PASS' if frontend_accessible else '❌ FAIL'}")

    if backend_healthy and frontend_accessible:
        print("\n🎉 All basic tests passed!")
        return True
    else:
        print("\n⚠️  Some tests failed. Check the services are running.")
        return False


def main():
    """Main test function"""
    print("🚀 Image Processing Application - Test Suite")
    print("=" * 50)

    # Display current configuration
    print("📋 Current Configuration:")
    print(f"  - Backend: {settings.API_HOST}:{settings.API_PORT}")
    print(f"  - Frontend: {settings.FRONTEND_HOST}:{settings.FRONTEND_PORT}")
    print(f"  - Backend URL: {settings.BACKEND_URL}")
    print()

    # Check if services are running
    print("Checking if services are running...")
    print("Make sure to start the application first:")
    print("  uv run main.py dev")
    print()

    # Run tests
    success = run_basic_tests()

    if not success:
        print("\n💡 To start the application:")
        print("  uv run main.py dev")
        print("\n💡 To start individual services:")
        print("  uv run main.py backend")
        print("  uv run main.py frontend")
        sys.exit(1)

    print("\n✨ Ready for additional tests!")
    print("You can add more specific tests to this script.")

    print("\n🔗 Service URLs:")
    print(f"  - Backend API: http://{settings.API_HOST}:{settings.API_PORT}")
    print(
        f"  - Frontend App: http://{settings.FRONTEND_HOST}:{settings.FRONTEND_PORT}")
    print(f"  - API Docs: http://{settings.API_HOST}:{settings.API_PORT}/docs")
    print(
        f"  - Health Check: http://{settings.API_HOST}:{settings.API_PORT}/health")


if __name__ == "__main__":
    main()
