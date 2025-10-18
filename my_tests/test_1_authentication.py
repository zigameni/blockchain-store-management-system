import requests
import json
import sys
import time

# Removed subprocess and os imports as they are no longer needed for Docker

# --- Configuration ---
BASE_URL = "http://localhost:5000"
# Global variable to store the access token for the delete test
ACCESS_TOKEN = ""


# --- Helper Functions ---

def run_test(test_num, test_name, method, endpoint, data, expected_status, expected_body_part=None, headers=None):
    """
    Executes a single API test, verifies the result, and prints the outcome.
    """
    global ACCESS_TOKEN

    url = f"{BASE_URL}{endpoint}"
    data_json = json.dumps(data) if data else None

    print(f"\n--- Test {test_num}: {test_name} ---")
    print(f"  URL: {url}")
    print(f"  Method: {method}")
    if data:
        print(f"  Data: {data_json}")

    # Set default headers if none are provided
    if headers is None:
        headers = {'Content-Type': 'application/json'}

    try:
        if method == 'POST':
            response = requests.post(url, data=data_json, headers=headers, timeout=10)  # Added timeout
        else:
            print(f"\033[91mERROR: Unsupported HTTP method: {method}\033[0m")
            return False

    except requests.exceptions.ConnectionError:
        print(
            f"\033[91m[FAIL] Test {test_num}: Connection Error. Is your Flask application running at {BASE_URL}?\033[0m")
        return False
    except requests.exceptions.ReadTimeout:
        print(f"\033[91m[FAIL] Test {test_num}: Request timed out after 10 seconds.\033[0m")
        return False
    except Exception as e:
        print(f"\033[91m[FAIL] Test {test_num}: An unexpected error occurred: {e}\033[0m")
        return False

    status_code = response.status_code
    response_body = response.text

    print(f"  Expected Status: {expected_status}")
    print(f"  Actual Status: {status_code}")
    print(f"  Response Body: {response_body.strip()}")

    passed = True

    # 1. Check Status Code
    if status_code != expected_status:
        print(f"\033[91m[FAIL] Status mismatch. Expected {expected_status}, got {status_code}\033[0m")
        passed = False

    # 2. Check Body Content
    if expected_body_part is not None:
        if expected_body_part == "" and response_body.strip() != "":
            # Expecting empty body (200 OK), but got content
            print(f"\033[91m[FAIL] Body expected to be empty, but got content: {response_body.strip()}\033[0m")
            passed = False
        elif expected_body_part and expected_body_part not in response_body:
            # Expecting specific content (e.g., error message or token part), but it's missing
            print(f"\033[91m[FAIL] Body mismatch. Expected to contain: '{expected_body_part}'\033[0m")
            passed = False

    if passed:
        print(f"\033[92m[SUCCESS] Test {test_num}: {test_name} passed.\033[0m")

        # Logic to save the access token for Test 10
        if 'accessToken' in response_body and test_num in (7, 9):
            try:
                data = response.json()
                # Overwrite the token, as it's only needed for the final delete test
                global ACCESS_TOKEN
                ACCESS_TOKEN = data.get('accessToken', "")
            except json.JSONDecodeError:
                print("Warning: Could not decode JSON response to save token.")

    return passed


# --- Main Execution ---

def main():
    print("\033[92m### Flask API Authentication Test Script (Python) ###\033[0m\n")

    try:
        # Check for requests module
        import requests
    except ImportError:
        print("The 'requests' library is required. Please install it with: \033[1mpip install requests\033[0m")
        sys.exit(1)

    # --- Test Control Array ---
    # To skip a test, simply comment out or remove its number from this list.
    TESTS_TO_RUN = [
        1,  # Successful Customer Registration
        2,  # Missing Field Error
        3,  # Invalid Email Error
        4,  # Short Password Error
        5,  # Duplicate Email Error
        6,  # Successful Courier Registration
        7,  # Successful Login (Customer)
        8,  # Invalid Credentials
        9,  # Login as Owner
        10  # Delete Account (Requires 7 or 9 to run first)
    ]

    print(f"NOTE: Assuming the Flask application is already running at {BASE_URL}")
    print(f"Running {len(TESTS_TO_RUN)} tests: {TESTS_TO_RUN}")
    time.sleep(1)

    # --- Tests 1-9 (Conditional Execution) ---

    if 1 in TESTS_TO_RUN:
        run_test(1, "Successful Customer Registration", 'POST', '/register_customer',
                 {"forename": "John", "surname": "Doe", "email": "john@example.com", "password": "password123"},
                 200, "")

    if 2 in TESTS_TO_RUN:
        run_test(2, "Missing Field Error", 'POST', '/register_customer',
                 {"forename": "John", "surname": "Doe", "password": "password123"},
                 400, "Field email is missing.")

    if 3 in TESTS_TO_RUN:
        run_test(3, "Invalid Email Error", 'POST', '/register_customer',
                 {"forename": "John", "surname": "Doe", "email": "invalidemail", "password": "password123"},
                 400, "Invalid email.")

    if 4 in TESTS_TO_RUN:
        run_test(4, "Short Password Error", 'POST', '/register_customer',
                 {"forename": "John", "surname": "Doe", "email": "john2@example.com", "password": "pass"},
                 400, "Invalid password.")

    if 5 in TESTS_TO_RUN:
        run_test(5, "Duplicate Email Error", 'POST', '/register_customer',
                 {"forename": "Jane", "surname": "Doe", "email": "john@example.com", "password": "password123"},
                 400, "Email already exists.")

    if 6 in TESTS_TO_RUN:
        run_test(6, "Successful Courier Registration", 'POST', '/register_courier',
                 {"forename": "Bob", "surname": "Driver", "email": "bob@courier.com", "password": "password123"},
                 200, "")

    if 7 in TESTS_TO_RUN:
        run_test(7, "Successful Login (Customer) - TOKEN SAVED HERE", 'POST', '/login',
                 {"email": "john@example.com", "password": "password123"},
                 200, "accessToken")

    if 8 in TESTS_TO_RUN:
        run_test(8, "Invalid Credentials", 'POST', '/login',
                 {"email": "john@example.com", "password": "wrongpassword"},
                 400, "Invalid credentials.")

    if 9 in TESTS_TO_RUN:
        run_test(9, "Login as Owner", 'POST', '/login',
                 {"email": "onlymoney@gmail.com", "password": "evenmoremoney"},
                 200, "accessToken")

    # --- Test 10: Delete Account (Multi-step) ---
    if 10 in TESTS_TO_RUN:
        print("\n--- Test 10: Delete Account (Multi-step) ---")

        # Test 10 relies on the token saved from Test 7 or Test 9.
        if not ACCESS_TOKEN:
            print(
                "\033[91m[FAIL] Step 10a (Prerequisite): No access token available to test deletion. Did Test 7 or 9 run and pass?\033[0m")
        else:
            print("  Token retrieved successfully for deletion.")

            # 2. Delete with token
            url = f"{BASE_URL}/delete"
            headers = {
                'Authorization': f'Bearer {ACCESS_TOKEN}',
                'Content-Type': 'application/json'
            }

            try:
                # We don't send a body for delete
                response = requests.post(url, headers=headers)
                delete_status = response.status_code

                print(f"  Delete Status Code: {delete_status}")

                if delete_status == 200 and response.text.strip() == "":
                    print("\033[92m[SUCCESS] Test 10: Delete Account passed. Account deleted.\033[0m")
                else:
                    print(
                        f"\033[91m[FAIL] Test 10: Delete Account Status/Body mismatch. Expected 200 and empty body, got {delete_status} and body: {response.text.strip()}\033[0m")

            except requests.exceptions.ConnectionError:
                print(f"\033[91m[FAIL] Test 10: Connection Error during delete request.\033[0m")
            except Exception as e:
                print(f"\033[91m[FAIL] Test 10: An unexpected error occurred during delete: {e}\033[0m")

    print("\n--- Testing Complete ---")


if __name__ == '__main__':
    main()
