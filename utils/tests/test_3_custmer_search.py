import requests
import json
import sys
import time

# --- Configuration ---
AUTH_URL = "http://localhost:5000"
CUSTOMER_URL = "http://localhost:5002"

# Global variables
CUSTOMER_TOKEN = ""
OWNER_TOKEN = ""


# --- Helper Functions ---

def run_test(test_num, test_name, method, endpoint, expected_status,
             expected_content=None, check_structure=False, headers=None):
    """
    Executes a single API test, verifies the result, and prints the outcome.
    """
    url = f"{CUSTOMER_URL}{endpoint}"

    print(f"\n--- Test {test_num}: {test_name} ---")
    print(f"  URL: {url}")
    print(f"  Method: {method}")

    try:
        if method == 'GET':
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

    # Try to parse JSON for prettier display
    try:
        json_data = response.json()
        print(f"  Response Body: {json.dumps(json_data, indent=2)}")
    except:
        print(f"  Response Body: {response_body.strip()}")

    passed = True

    # Check Status Code
    if status_code != expected_status:
        print(f"\033[91m[FAIL] Status mismatch. Expected {expected_status}, got {status_code}\033[0m")
        passed = False

    # Check Content
    if expected_content is not None:
        if expected_content not in response_body:
            print(f"\033[91m[FAIL] Body mismatch. Expected to contain: '{expected_content}'\033[0m")
            passed = False

    # Check structure if needed
    if check_structure and passed:
        try:
            data = response.json()
            if 'categories' not in data or 'products' not in data:
                print(f"\033[91m[FAIL] Response missing 'categories' or 'products' keys\033[0m")
                passed = False
            elif not isinstance(data['categories'], list) or not isinstance(data['products'], list):
                print(f"\033[91m[FAIL] 'categories' or 'products' are not lists\033[0m")
                passed = False
            else:
                print(f"  Structure valid: {len(data['categories'])} categories, {len(data['products'])} products")
        except json.JSONDecodeError:
            print(f"\033[91m[FAIL] Response is not valid JSON\033[0m")
            passed = False

    if passed:
        print(f"\033[92m[SUCCESS] Test {test_num}: {test_name} passed.\033[0m")

    return passed


def register_and_login_customer():
    """Register and login as customer, save the access token."""
    global CUSTOMER_TOKEN

    print("\n=== Registering and Logging in as Customer ===")

    # Register
    reg_url = f"{AUTH_URL}/register_customer"
    reg_data = {
        "forename": "Alice",
        "surname": "Smith",
        "email": "alice@example.com",
        "password": "password123"
    }

    try:
        reg_response = requests.post(reg_url, json=reg_data, timeout=10)
        print(f"Customer registration status: {reg_response.status_code}")
        if reg_response.status_code == 400 and "Email already exists" in reg_response.text:
            print("Customer already registered, proceeding to login...")

        # Login
        login_url = f"{AUTH_URL}/login"
        login_data = {"email": "alice@example.com", "password": "password123"}
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


def verify_product_structure(test_num):
    """Special test to verify product structure in detail."""
    print(f"\n--- Test {test_num}: Verify Product Structure ---")

    url = f"{CUSTOMER_URL}/search?name=Laptop"
    headers = {'Authorization': f'Bearer {CUSTOMER_TOKEN}'}

    try:
        response = requests.get(url, headers=headers, timeout=10)

        if response.status_code != 200:
            print(f"\033[91m[FAIL] Status code: {response.status_code}\033[0m")
            return False

        data = response.json()
        print(f"  Response: {json.dumps(data, indent=2)}")

        # Check structure
        passed = True

        if 'categories' not in data or 'products' not in data:
            print(f"\033[91m[FAIL] Missing 'categories' or 'products' keys\033[0m")
            return False

        if len(data['products']) == 0:
            print(f"\033[91m[FAIL] No products returned for 'Laptop'\033[0m")
            return False

        product = data['products'][0]
        required_fields = ['id', 'name', 'price', 'categories']

        for field in required_fields:
            if field not in product:
                print(f"\033[91m[FAIL] Product missing field: '{field}'\033[0m")
                passed = False

        # Verify types
        if 'id' in product and not isinstance(product['id'], int):
            print(f"\033[91m[FAIL] Product 'id' is not an integer\033[0m")
            passed = False

        if 'name' in product and not isinstance(product['name'], str):
            print(f"\033[91m[FAIL] Product 'name' is not a string\033[0m")
            passed = False

        if 'price' in product and not isinstance(product['price'], (int, float)):
            print(f"\033[91m[FAIL] Product 'price' is not a number\033[0m")
            passed = False

        if 'categories' in product and not isinstance(product['categories'], list):
            print(f"\033[91m[FAIL] Product 'categories' is not a list\033[0m")
            passed = False

        if passed:
            print(f"\033[92m[SUCCESS] Test {test_num}: Product structure is valid.\033[0m")

        return passed

    except Exception as e:
        print(f"\033[91m[FAIL] Error: {e}\033[0m")
        return False


# --- Main Execution ---

def main():
    print("\033[92m### Flask Customer Search Test Script (Python) ###\033[0m\n")

    # Test Control Array
    TESTS_TO_RUN = [
        1,  # Search All Products (No Filters)
        2,  # Search by Product Name
        3,  # Search by Partial Product Name
        4,  # Search by Category
        5,  # Search by Partial Category Name
        6,  # Search by Both Name and Category
        7,  # Search with No Results (Name)
        8,  # Search with No Results (Category)
        9,  # Verify Product Structure
        10,  # Case-Insensitive Search
        11,  # Search Multiple Words
        12,  # Unauthorized Access (Owner)
        13,  # Search Products with Multiple Categories
        14,  # Verify All Categories Returned
    ]

    print(f"NOTE: Assuming applications are running at {AUTH_URL} and {CUSTOMER_URL}")
    print(f"Running {len(TESTS_TO_RUN)} tests: {TESTS_TO_RUN}")
    time.sleep(1)

    # Login as customer first
    if not register_and_login_customer():
        print("\033[91mFailed to login as customer. Exiting.\033[0m")
        sys.exit(1)

    customer_headers = {
        'Authorization': f'Bearer {CUSTOMER_TOKEN}'
    }

    # --- Test 1: Search All Products (No Filters) ---
    if 1 in TESTS_TO_RUN:
        run_test(1, "Search All Products (No Filters)", 'GET', '/search',
                 200, check_structure=True, headers=customer_headers)

    # --- Test 2: Search by Product Name ---
    if 2 in TESTS_TO_RUN:
        run_test(2, "Search by Product Name", 'GET', '/search?name=Laptop',
                 200, '"name": "Laptop"', check_structure=True, headers=customer_headers)

    # --- Test 3: Search by Partial Product Name ---
    if 3 in TESTS_TO_RUN:
        run_test(3, "Search by Partial Product Name", 'GET', '/search?name=o',
                 200, check_structure=True, headers=customer_headers)

    # --- Test 4: Search by Category ---
    if 4 in TESTS_TO_RUN:
        run_test(4, "Search by Category", 'GET', '/search?category=Electronics',
                 200, '"Electronics"', check_structure=True, headers=customer_headers)

    # --- Test 5: Search by Partial Category Name ---
    if 5 in TESTS_TO_RUN:
        run_test(5, "Search by Partial Category Name", 'GET', '/search?category=Book',
                 200, check_structure=True, headers=customer_headers)

    # --- Test 6: Search by Both Name and Category ---
    if 6 in TESTS_TO_RUN:
        run_test(6, "Search by Both Name and Category", 'GET',
                 '/search?name=Laptop&category=Electronics',
                 200, '"name": "Laptop"', check_structure=True, headers=customer_headers)

    # --- Test 7: Search with No Results (Name) ---
    if 7 in TESTS_TO_RUN:
        run_test(7, "Search with No Results (Name)", 'GET',
                 '/search?name=NonExistentProduct',
                 200, '"categories": []', headers=customer_headers)

    # --- Test 8: Search with No Results (Category) ---
    if 8 in TESTS_TO_RUN:
        run_test(8, "Search with No Results (Category)", 'GET',
                 '/search?category=NonExistentCategory',
                 200, '"products": []', headers=customer_headers)

    # --- Test 9: Verify Product Structure ---
    if 9 in TESTS_TO_RUN:
        verify_product_structure(9)

    # --- Test 10: Case-Insensitive Search ---
    if 10 in TESTS_TO_RUN:
        run_test(10, "Case-Insensitive Search", 'GET', '/search?name=laptop',
                 200, '"name": "Laptop"', check_structure=True, headers=customer_headers)

    # --- Test 11: Search Multiple Words ---
    if 11 in TESTS_TO_RUN:
        run_test(11, "Search Multiple Words", 'GET', '/search?name=Wireless%20Mouse',
                 200, '"Wireless Mouse"', check_structure=True, headers=customer_headers)

    # --- Test 12: Unauthorized Access (Owner) ---
    if 12 in TESTS_TO_RUN:
        if login_as_owner():
            owner_headers = {
                'Authorization': f'Bearer {OWNER_TOKEN}'
            }
            run_test(12, "Unauthorized Access (Owner)", 'GET', '/search',
                     403, "Unauthorized.", headers=owner_headers)

    # --- Test 13: Search Products with Multiple Categories ---
    if 13 in TESTS_TO_RUN:
        run_test(13, "Search Products with Multiple Categories", 'GET',
                 '/search?name=Headphones',
                 200, check_structure=True, headers=customer_headers)

    # --- Test 14: Verify All Categories Returned ---
    if 14 in TESTS_TO_RUN:
        print(f"\n--- Test 14: Verify All Categories Returned ---")
        url = f"{CUSTOMER_URL}/search"

        try:
            response = requests.get(url, headers=customer_headers, timeout=10)

            if response.status_code == 200:
                data = response.json()
                num_categories = len(data.get('categories', []))
                num_products = len(data.get('products', []))

                print(f"  Categories count: {num_categories}")
                print(f"  Products count: {num_products}")

                if num_categories > 0 and num_products > 0:
                    print(
                        f"\033[92m[SUCCESS] Test 14: Returned {num_categories} categories and {num_products} products.\033[0m")
                else:
                    print(f"\033[91m[FAIL] Test 14: No categories or products returned.\033[0m")
            else:
                print(f"\033[91m[FAIL] Test 14: Status code: {response.status_code}\033[0m")
        except Exception as e:
            print(f"\033[91m[FAIL] Test 14: Error: {e}\033[0m")

    print("\n--- Testing Complete ---")


if __name__ == '__main__':
    main()