import requests
import json
import sys
import time
import os

# --- Configuration ---
AUTH_URL = "http://localhost:5000"
PRODUCT_URL = "http://localhost:5001"

# Global variables
OWNER_TOKEN = ""
CUSTOMER_TOKEN = ""


# --- Helper Functions ---

def create_csv_file(filename, content):
    """Creates a CSV file with the given content."""
    with open(filename, 'w') as f:
        f.write(content)
    print(f"  Created file: {filename}")


def cleanup_csv_files():
    """Remove test CSV files."""
    csv_files = ['products.csv', 'bad_products.csv', 'duplicate_products.csv',
                 'more_products.csv', 'test_products.csv']
    for file in csv_files:
        if os.path.exists(file):
            os.remove(file)


def run_test(test_num, test_name, method, endpoint, expected_status,
             expected_body_part=None, headers=None, files=None, data=None):
    """
    Executes a single API test, verifies the result, and prints the outcome.
    """
    url = f"{PRODUCT_URL}{endpoint}"

    print(f"\n--- Test {test_num}: {test_name} ---")
    print(f"  URL: {url}")
    print(f"  Method: {method}")

    try:
        if method == 'POST':
            if files:
                # For file uploads, don't set Content-Type in headers
                upload_headers = {'Authorization': headers.get('Authorization')} if headers else {}
                response = requests.post(url, headers=upload_headers, files=files, timeout=10)
            else:
                response = requests.post(url, json=data, headers=headers, timeout=10)
        elif method == 'GET':
            response = requests.get(url, headers=headers, timeout=10)
        else:
            print(f"\033[91mERROR: Unsupported HTTP method: {method}\033[0m")
            return False

    except requests.exceptions.ConnectionError:
        print(f"\033[91m[FAIL] Test {test_num}: Connection Error. Is your application running at {url}?\033[0m")
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

    # Check Status Code
    if status_code != expected_status:
        print(f"\033[91m[FAIL] Status mismatch. Expected {expected_status}, got {status_code}\033[0m")
        passed = False

    # Check Body Content
    if expected_body_part is not None:
        if expected_body_part == "" and response_body.strip() != "":
            print(f"\033[91m[FAIL] Body expected to be empty, but got content: {response_body.strip()}\033[0m")
            passed = False
        elif expected_body_part and expected_body_part not in response_body:
            print(f"\033[91m[FAIL] Body mismatch. Expected to contain: '{expected_body_part}'\033[0m")
            passed = False

    if passed:
        print(f"\033[92m[SUCCESS] Test {test_num}: {test_name} passed.\033[0m")

    return passed


def login_as_owner():
    """Login as owner and save the access token."""
    global OWNER_TOKEN

    print("\n=== Logging in as Owner ===")
    url = f"{AUTH_URL}/login"
    data = {"email": "onlymoney@gmail.com", "password": "evenmoremoney"}

    try:
        response = requests.post(url, json=data, timeout=10)
        if response.status_code == 200:
            token_data = response.json()
            OWNER_TOKEN = token_data.get('accessToken', '')
            print(f"\033[92mOwner login successful. Token saved.\033[0m")
            return True
        else:
            print(f"\033[91mOwner login failed with status {response.status_code}\033[0m")
            return False
    except Exception as e:
        print(f"\033[91mOwner login error: {e}\033[0m")
        return False


def register_and_login_customer():
    """Register and login as customer, save the access token."""
    global CUSTOMER_TOKEN

    print("\n=== Registering and Logging in as Customer ===")

    # Register
    reg_url = f"{AUTH_URL}/register_customer"
    reg_data = {
        "forename": "Test",
        "surname": "User",
        "email": "test@example.com",
        "password": "password123"
    }

    try:
        reg_response = requests.post(reg_url, json=reg_data, timeout=10)
        print(f"Customer registration status: {reg_response.status_code}")

        # Login
        login_url = f"{AUTH_URL}/login"
        login_data = {"email": "test@example.com", "password": "password123"}
        login_response = requests.post(login_url, json=login_data, timeout=10)

        if login_response.status_code == 200:
            token_data = login_response.json()
            CUSTOMER_TOKEN = token_data.get('accessToken', '')
            print(f"\033[92mCustomer login successful. Token saved.\033[0m")
            return True
        else:
            print(f"\033[91mCustomer login failed with status {login_response.status_code}\033[0m")
            return False
    except Exception as e:
        print(f"\033[91mCustomer registration/login error: {e}\033[0m")
        return False


# --- Main Execution ---

def main():
    print("\033[92m### Flask Product Management Test Script (Python) ###\033[0m\n")

    # Clean up any existing CSV files from previous runs
    cleanup_csv_files()

    # Test Control Array
    TESTS_TO_RUN = [
        1,  # Upload Products (Success)
        2,  # Missing File Error
        3,  # Incorrect Number of Fields
        4,  # Invalid Price (Not a Number)
        5,  # Invalid Price (Negative)
        6,  # Duplicate Product Name
        7,  # Add More Products
        8,  # Unauthorized Access (Customer)
        9,  # Product Statistics (Empty)
        10  # Category Statistics (Empty)
    ]

    print(f"NOTE: Assuming applications are running at {AUTH_URL} and {PRODUCT_URL}")
    print(f"Running {len(TESTS_TO_RUN)} tests: {TESTS_TO_RUN}")
    time.sleep(1)

    # Login as owner first
    if not login_as_owner():
        print("\033[91mFailed to login as owner. Exiting.\033[0m")
        sys.exit(1)

    owner_headers = {
        'Authorization': f'Bearer {OWNER_TOKEN}',
        'Content-Type': 'application/json'
    }

    # --- Test 1: Upload Products (Success) ---
    if 1 in TESTS_TO_RUN:
        csv_content = """Electronics|Gadgets,Laptop,85000
Electronics,Wireless Mouse,2500
Electronics|Audio,Headphones,4500
Home|Kitchen,Blender,3500
Sports|Fitness,Yoga Mat,1200"""
        create_csv_file('products.csv', csv_content)

        with open('products.csv', 'rb') as f:
            files = {'file': ('products.csv', f, 'text/csv')}
            run_test(1, "Upload Products (Success)", 'POST', '/update',
                     200, "", headers=owner_headers, files=files)

    # --- Test 2: Missing File Error ---
    if 2 in TESTS_TO_RUN:
        run_test(2, "Missing File Error", 'POST', '/update',
                 400, "Field file is missing.", headers=owner_headers)

    # --- Test 3: Incorrect Number of Fields ---
    if 3 in TESTS_TO_RUN:
        csv_content = "Electronics,Laptop"
        create_csv_file('bad_products.csv', csv_content)

        with open('bad_products.csv', 'rb') as f:
            files = {'file': ('bad_products.csv', f, 'text/csv')}
            run_test(3, "Incorrect Number of Fields", 'POST', '/update',
                     400, "Incorrect number of values on line 0.",
                     headers=owner_headers, files=files)

    # --- Test 4: Invalid Price (Not a Number) ---
    if 4 in TESTS_TO_RUN:
        csv_content = "Electronics,Tablet,NotANumber"
        create_csv_file('bad_products.csv', csv_content)

        with open('bad_products.csv', 'rb') as f:
            files = {'file': ('bad_products.csv', f, 'text/csv')}
            run_test(4, "Invalid Price (Not a Number)", 'POST', '/update',
                     400, "Incorrect price on line 0.",
                     headers=owner_headers, files=files)

    # --- Test 5: Invalid Price (Negative) ---
    if 5 in TESTS_TO_RUN:
        csv_content = "Electronics,Tablet,-100"
        create_csv_file('bad_products.csv', csv_content)

        with open('bad_products.csv', 'rb') as f:
            files = {'file': ('bad_products.csv', f, 'text/csv')}
            run_test(5, "Invalid Price (Negative)", 'POST', '/update',
                     400, "Incorrect price on line 0.",
                     headers=owner_headers, files=files)

    # --- Test 6: Duplicate Product Name ---
    if 6 in TESTS_TO_RUN:
        csv_content = "Electronics,Laptop,90000"
        create_csv_file('duplicate_products.csv', csv_content)

        with open('duplicate_products.csv', 'rb') as f:
            files = {'file': ('duplicate_products.csv', f, 'text/csv')}
            run_test(6, "Duplicate Product Name", 'POST', '/update',
                     400, "Product Laptop already exists.",
                     headers=owner_headers, files=files)

    # --- Test 7: Add More Products ---
    if 7 in TESTS_TO_RUN:
        csv_content = """Books|Fiction,Novel,1500
Books|NonFiction,Biography,2000
Clothing|Men,T-Shirt,800
Clothing|Women,Dress,2500
Electronics|Gaming,Gaming Console,45000"""
        create_csv_file('more_products.csv', csv_content)

        with open('more_products.csv', 'rb') as f:
            files = {'file': ('more_products.csv', f, 'text/csv')}
            run_test(7, "Add More Products", 'POST', '/update',
                     200, "", headers=owner_headers, files=files)

    # --- Test 8: Unauthorized Access (Customer) ---
    if 8 in TESTS_TO_RUN:
        if register_and_login_customer():
            csv_content = "Test,TestProduct,100"
            create_csv_file('test_products.csv', csv_content)

            customer_headers = {
                'Authorization': f'Bearer {CUSTOMER_TOKEN}',
                'Content-Type': 'application/json'
            }

            with open('test_products.csv', 'rb') as f:
                files = {'file': ('test_products.csv', f, 'text/csv')}
                run_test(8, "Unauthorized Access (Customer)", 'POST', '/update',
                         403, "Unauthorized.", headers=customer_headers, files=files)

    # --- Test 9: Product Statistics (Empty) ---
    if 9 in TESTS_TO_RUN:
        run_test(9, "Product Statistics (Empty)", 'GET', '/product_statistics',
                 200, '"statistics": []', headers=owner_headers)

    # --- Test 10: Category Statistics (Empty) ---
    if 10 in TESTS_TO_RUN:
        run_test(10, "Category Statistics (Empty)", 'GET', '/category_statistics',
                 200, '"statistics": []', headers=owner_headers)

    print("\n--- Testing Complete ---")

    # Cleanup CSV files
    print("\nCleaning up test CSV files...")
    cleanup_csv_files()
    print("Cleanup complete.")


if __name__ == '__main__':
    main()
