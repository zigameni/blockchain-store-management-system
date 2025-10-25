import json
import re

import bcrypt
from eth_account import Account
from web3 import Web3, HTTPProvider

from configuration import BLOCKCHAIN_URL


def hash_password(password):
    """Hash a password using bcrypt"""
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

def verify_password(password, hashed_password):
    """Verify password against hashed password"""
    return bcrypt.checkpw(password.encode('utf-8'), hashed_password.encode('utf-8'))

def is_valid_email(email):
    """Validate email format using regex"""
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email)

def get_web3():
    """Get web3 instance"""
    return Web3(HTTPProvider(BLOCKCHAIN_URL))

def send_transaction(transaction, private_key):
    """Sign and send transaction via blockchain"""
    web3 = get_web3()
    signed_transaction = web3.eth.account.sign_transaction(transaction, private_key)
    raw_tx = getattr(signed_transaction, 'rawTransaction', None) or signed_transaction.raw_transaction
    transaction_hash = web3.eth.send_raw_transaction(raw_tx)
    receipt = web3.eth.wait_for_transaction_receipt(transaction_hash)
    return receipt

def read_file(path):
    """Read file contents"""
    with open(path, "r") as file:
        return file.read()

def get_owner_account():
    """
    Get owner's Ethereum account address and private key.
    Also ensures the owner account has sufficient funds.
    """

    web3 = get_web3()

    try:
        with open("owner_account.json", "r") as file:
            keystore = json.load(file)
    except FileNotFoundError:
        raise Exception("Owner account file not found")

    # decrypt with password
    try:
        private_key_bytes = Account.decrypt(keystore, 'iepblockchain')
        private_key = private_key_bytes.hex()
    except Exception as e:
        raise Exception(f"Failed to decrypt owner account: {str(e)}")

    # get address
    address = web3.to_checksum_address(keystore['address'])

    # check balance
    balance = web3.eth.get_balance(address)

    # if balance is low, fund from ganache account[0]
    if balance <= web3.to_wei(1, "ether"):
        try:
            # transfer to 10 eth from first Ganache account
            tx_hash = web3.eth.send_transaction({
                "from": web3.eth.accounts[0],
                "to": address,
                "value": web3.to_wei(10, "ether"),
                "gas": 210000,
                "gasPrice": web3.eth.gas_price
            })
            web3.eth.wait_for_transaction_receipt(tx_hash)
            print(f"Funded owner account {address} with 10 ETH")
        except Exception as e:
            print(f"Warning: Could not fund owner account: {str(e)}")

    return (address, private_key)

def is_valid_address(address):
    """Validate eth address format"""
    if not address or not isinstance(address, str):
        return False

    # check if it's a valid hex string and correct length
    if not address.startswith("0x"):
        address = "0x" + address

    if len(address) != 42:
        return False

    try:
        # try to convert to checksum address
        web3 = get_web3()
        web3.to_checksum_address(address)
        return True
    except:
        return False

