"""Test script to debug signup issues."""

import requests
import json

API_BASE = "http://localhost:8000"

# Test data
test_data = {
    "email": "afsheen081@yahoo.com",
    "password": "Pakistan12",
    "name": "afsheen"
}

print("Testing signup endpoint...")
print(f"URL: {API_BASE}/api/auth/register")
print(f"Data: {json.dumps(test_data, indent=2)}")
print("-" * 50)

try:
    response = requests.post(
        f"{API_BASE}/api/auth/register",
        json=test_data,
        headers={"Content-Type": "application/json"}
    )

    print(f"Status Code: {response.status_code}")
    print(f"Response: {response.text}")

    if response.status_code == 201:
        print("\n✓ Signup successful!")
        response_data = response.json()
        print(f"User ID: {response_data['user']['id']}")
        print(f"Email: {response_data['user']['email']}")
        print(f"Token: {response_data['token'][:50]}...")
    else:
        print(f"\n✗ Signup failed with status {response.status_code}")

except requests.exceptions.ConnectionError:
    print("✗ Error: Could not connect to backend server.")
    print("Make sure the backend is running on http://localhost:8000")
except Exception as e:
    print(f"✗ Error: {str(e)}")
