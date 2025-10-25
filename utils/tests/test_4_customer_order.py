import requests
import json
import sys
import time

# --- Configuration ---
AUTH_URL = "http://localhost:5000"
CUSTOMER_URL = "http://localhost:5002"

# Global variables
CUSTOMER_TOKEN = ""
CUSTOMER2_TOKEN = ""
PRODUCT_IDS = []


# --- Helper Functions ---

def run_test(test_num, test_name, method, endpoint, data, expected_status,
             expected_content=None, headers=None):
    """
    Executes a single API test, verifies the result, and prints the outcome.
    """
    url = f"{CUSTOMER_URL}{endpoint}"

    print(f"\n--- Test {test_num}: {test_name} ---")
    print(f"  URL: {url}")
    print(f"  Method: {method}")
    if data:
        print(f"  Data: {json.dumps(data, indent=2)}")

    try:
        if method == 'POST':
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

    if passed:
        print(f"\033[92m[SUCCESS] Test {test_num}: {test_name} passed.\033[0m")

    return passed


def login_customer(email, password):
    """Login as customer and return the access token."""
    print(f"\n=== Logging in as {email} ===")

    # Try to register first (in case user doesn't exist)
    reg_url = f"{AUTH_URL}/register_customer"
    name_parts = email.split('@')[0].split('.')
    forename = name_parts[0].capitalize()
    surname = name_parts[1].capitalize() if len(name_parts) > 1 else "User"

    reg_data = {
        "forename": forename,
        "surname": surname,
        "email": email,
        "password": password
    }

    try:
        reg_response = requests.post(reg_url, json=reg_data, timeout=10)
        if reg_response.status_code == 400 and "Email already exists" in reg_response.text:
            print(f"Customer {email} already registered, proceeding to login...")
        else:
            print(f"Customer registration status: {reg_response.status_code}")

        # Login
        login_url = f"{AUTH_URL}/login"
        login_data = {"email": email, "password": password}
        login_response = requests.post(login_url, json=login_data, timeout=10)

        if login_response.status_code == 200:
            token_data = login_response.json()
            token = token_data.get('accessToken', '')
            print(f"\033[92mLogin successful for {email}. Token saved.\033[0m")
            return token
        else:
            print(f"\033[91mLogin failed with status {login_response.status_code}\033[0m")
            return None
    except Exception as e:
        print(f"\033[91mLogin error: {e}\033[0m")
        return None


def get_product_ids():
    """Get product IDs from search endpoint."""
    global PRODUCT_IDS

    print("\n=== Fetching Product IDs ===")
    url = f"{CUSTOMER_URL}/search"
    headers = {'Authorization': f'Bearer {CUSTOMER_TOKEN}'}

    try:
        response = requests.get(url, headers=headers, timeout=10)
        if response.status_code == 200:
            data = response.json()
            products = data.get('products', [])
            PRODUCT_IDS = [p['id'] for p in products]
            print(f"Found {len(PRODUCT_IDS)} products with IDs: {PRODUCT_IDS}")
            return True
        else:
            print(f"\033[91mFailed to get products. Status: {response.status_code}\033[0m")
            return False
    except Exception as e:
        print(f"\033[91mError getting products: {e}\033[0m")
        return False


def verify_order_created(test_num, response_body):
    """Verify that an order ID was returned."""
    try:
        data = json.loads(response_body)
        if 'id' in data and isinstance(data['id'], int) and data['id'] > 0:
            print(f"  Order ID {data['id']} created successfully")
            return True
        else:
            print(f"\033[91m[FAIL] Invalid order ID in response\033[0m")
            return False
    except:
        return False


# --- Main Execution ---

def main():
    print("\033[92m### Flask Customer Order Test Script (Python) ###\033[0m\n")

    global CUSTOMER_TOKEN, CUSTOMER2_TOKEN

    # Test Control Array
    TESTS_TO_RUN = [
        1,  # Create Valid Order (Single Product)
        2,  # Create Valid Order (Multiple Products)
        3,  # Missing requests Field
        4,  # Missing id Field
        5,  # Missing quantity Field
        6,  # Invalid Product ID (Not Integer)
        7,  # Invalid Product ID (Zero)
        8,  # Invalid Product ID (Negative)
        9,  # Invalid Quantity (Not Integer)
        10,  # Invalid Quantity (Zero)
        11,  # Invalid Quantity (Negative)
        12,  # Invalid Product (Doesn't Exist)
        13,  # Multiple Items with Error in Second Item
        14,  # Create Order as Different Customer
    ]

    print(f"NOTE: Assuming applications are running at {AUTH_URL} and {CUSTOMER_URL}")
    print(f"Running {len(TESTS_TO_RUN)} tests: {TESTS_TO_RUN}")
    time.sleep(1)

    # Login as first customer
    CUSTOMER_TOKEN = login_customer("alice@example.com", "password123")
    if not CUSTOMER_TOKEN:
        print("\033[91mFailed to login as alice@example.com. Exiting.\033[0m")
        sys.exit(1)

    # Get product IDs
    if not get_product_ids():
        print("\033[91mFailed to get product IDs. Make sure products are uploaded first.\033[0m")
        sys.exit(1)

    if len(PRODUCT_IDS) < 4:
        print(f"\033[93mWarning: Only {len(PRODUCT_IDS)} products found. Some tests may need adjustment.\033[0m")

    customer_headers = {
        'Authorization': f'Bearer {CUSTOMER_TOKEN}',
        'Content-Type': 'application/json'
    }

    # Use first available product IDs or fallback to sequential IDs
    product_id_1 = PRODUCT_IDS[0] if len(PRODUCT_IDS) > 0 else 1
    product_id_2 = PRODUCT_IDS[1] if len(PRODUCT_IDS) > 1 else 2
    product_id_3 = PRODUCT_IDS[2] if len(PRODUCT_IDS) > 2 else 3
    product_id_4 = PRODUCT_IDS[3] if len(PRODUCT_IDS) > 3 else 4

    # --- Test 1: Create Valid Order (Single Product) ---
    if 1 in TESTS_TO_RUN:
        data = {
            "requests": [
                {"id": product_id_1, "quantity": 2}
            ]
        }
        response = run_test(1, "Create Valid Order (Single Product)", 'POST', '/order',
                            data, 200, '"id"', headers=customer_headers)

    # --- Test 2: Create Valid Order (Multiple Products) ---
    if 2 in TESTS_TO_RUN:
        data = {
            "requests": [
                {"id": product_id_1, "quantity": 1},
                {"id": product_id_2, "quantity": 3},
                {"id": product_id_3, "quantity": 2}
            ]
        }
        run_test(2, "Create Valid Order (Multiple Products)", 'POST', '/order',
                 data, 200, '"id"', headers=customer_headers)

    # --- Test 3: Missing requests Field ---
    if 3 in TESTS_TO_RUN:
        run_test(3, "Missing requests Field", 'POST', '/order',
                 {}, 400, "Field requests is missing.", headers=customer_headers)

    # --- Test 4: Missing id Field ---
    if 4 in TESTS_TO_RUN:
        data = {
            "requests": [
                {"quantity": 2}
            ]
        }
        run_test(4, "Missing id Field", 'POST', '/order',
                 data, 400, "Product id is missing for request number 0.", headers=customer_headers)

    # --- Test 5: Missing quantity Field ---
    if 5 in TESTS_TO_RUN:
        data = {
            "requests": [
                {"id": product_id_1}
            ]
        }
        run_test(5, "Missing quantity Field", 'POST', '/order',
                 data, 400, "Product quantity is missing for request number 0.", headers=customer_headers)

    # --- Test 6: Invalid Product ID (Not Integer) ---
    if 6 in TESTS_TO_RUN:
        data = {
            "requests": [
                {"id": "invalid", "quantity": 2}
            ]
        }
        run_test(6, "Invalid Product ID (Not Integer)", 'POST', '/order',
                 data, 400, "Invalid product id for request number 0.", headers=customer_headers)

    # --- Test 7: Invalid Product ID (Zero) ---
    if 7 in TESTS_TO_RUN:
        data = {
            "requests": [
                {"id": 0, "quantity": 2}
            ]
        }
        run_test(7, "Invalid Product ID (Zero)", 'POST', '/order',
                 data, 400, "Invalid product id for request number 0.", headers=customer_headers)

    # --- Test 8: Invalid Product ID (Negative) ---
    if 8 in TESTS_TO_RUN:
        data = {
            "requests": [
                {"id": -1, "quantity": 2}
            ]
        }
        run_test(8, "Invalid Product ID (Negative)", 'POST', '/order',
                 data, 400, "Invalid product id for request number 0.", headers=customer_headers)

    # --- Test 9: Invalid Quantity (Not Integer) ---
    if 9 in TESTS_TO_RUN:
        data = {
            "requests": [
                {"id": product_id_1, "quantity": "two"}
            ]
        }
        run_test(9, "Invalid Quantity (Not Integer)", 'POST', '/order',
                 data, 400, "Invalid product quantity for request number 0.", headers=customer_headers)

    # --- Test 10: Invalid Quantity (Zero) ---
    if 10 in TESTS_TO_RUN:
        data = {
            "requests": [
                {"id": product_id_1, "quantity": 0}
            ]
        }
        run_test(10, "Invalid Quantity (Zero)", 'POST', '/order',
                 data, 400, "Invalid product quantity for request number 0.", headers=customer_headers)

    # --- Test 11: Invalid Quantity (Negative) ---
    if 11 in TESTS_TO_RUN:
        data = {
            "requests": [
                {"id": product_id_1, "quantity": -5}
            ]
        }
        run_test(11, "Invalid Quantity (Negative)", 'POST', '/order',
                 data, 400, "Invalid product quantity for request number 0.", headers=customer_headers)

    # --- Test 12: Invalid Product (Doesn't Exist) ---
    if 12 in TESTS_TO_RUN:
        data = {
            "requests": [
                {"id": 9999, "quantity": 2}
            ]
        }
        run_test(12, "Invalid Product (Doesn't Exist)", 'POST', '/order',
                 data, 400, "Invalid product for request number 0.", headers=customer_headers)

    # --- Test 13: Multiple Items with Error in Second Item ---
    if 13 in TESTS_TO_RUN:
        data = {
            "requests": [
                {"id": product_id_1, "quantity": 2},
                {"id": 9999, "quantity": 1}
            ]
        }
        run_test(13, "Multiple Items with Error in Second Item", 'POST', '/order',
                 data, 400, "Invalid product for request number 1.", headers=customer_headers)

    # --- Test 14: Create Order as Different Customer ---
    if 14 in TESTS_TO_RUN:
        CUSTOMER2_TOKEN = login_customer("bob@example.com", "password123")

        if CUSTOMER2_TOKEN:
            customer2_headers = {
                'Authorization': f'Bearer {CUSTOMER2_TOKEN}',
                'Content-Type': 'application/json'
            }

            data = {
                "requests": [
                    {"id": product_id_4, "quantity": 1}
                ]
            }
            run_test(14, "Create Order as Different Customer", 'POST', '/order',
                     data, 200, '"id"', headers=customer2_headers)
        else:
            print("\033[91m[SKIP] Test 14: Could not login as second customer\033[0m")

    print("\n--- Testing Complete ---")
    print("\nNOTE: To verify orders in the database:")
    print("  1. Check the 'orders' table in Adminer")
    print("  2. Check the 'order_products' table for product associations")
    print("  3. Verify that prices are calculated correctly")


if __name__ == '__main__':
    main()