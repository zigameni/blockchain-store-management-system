#!/usr/bin/env python3
"""
Test script to verify blockchain connectivity
"""
from utilities import get_web3, get_owner_account


def test_blockchain_connection():
    print("=" * 50)
    print("Testing Blockchain Connection")
    print("=" * 50)

    # Test Web3 connection
    print("\n1. Testing Web3 connection...")
    try:
        web3 = get_web3()
        is_connected = web3.is_connected()
        print(f"   Connected: {is_connected}")

        if not is_connected:
            print("   ERROR: Not connected to blockchain!")
            return False
    except Exception as e:
        print(f"   ERROR: {str(e)}")
        return False

    # Get Ganache accounts
    print("\n2. Getting Ganache accounts...")
    try:
        accounts = web3.eth.accounts
        print(f"   Available accounts: {len(accounts)}")
        for i, account in enumerate(accounts[:3]):
            balance = web3.eth.get_balance(account)
            balance_eth = web3.from_wei(balance, 'ether')
            print(f"   Account {i}: {account}")
            print(f"   Balance: {balance_eth} ETH")
    except Exception as e:
        print(f"   ERROR: {str(e)}")
        return False

    # Test owner account
    print("\n3. Testing owner account...")
    try:
        owner_address, owner_private_key = get_owner_account()
        print(f"   Owner address: {owner_address}")
        print(f"   Private key: {owner_private_key[:10]}...")  # Show only first 10 chars

        balance = web3.eth.get_balance(owner_address)
        balance_eth = web3.from_wei(balance, 'ether')
        print(f"   Owner balance: {balance_eth} ETH")

        if balance_eth < 1:
            print("   WARNING: Owner balance is low!")
    except Exception as e:
        print(f"   ERROR: {str(e)}")
        return False

    # Test gas price
    print("\n4. Testing gas price...")
    try:
        gas_price = web3.eth.gas_price
        print(f"   Current gas price: {gas_price} wei")
    except Exception as e:
        print(f"   ERROR: {str(e)}")
        return False

    print("\n" + "=" * 50)
    print("All blockchain tests passed!")
    print("=" * 50)
    return True


if __name__ == "__main__":
    success = test_blockchain_connection()
    exit(0 if success else 1)