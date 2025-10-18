import re

import bcrypt
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
    """sign, send transaction via blockchain"""
    web3 = get_web3()
    signed_transaction = web3.eth.account.signTransaction(transaction, private_key)
    transaction_hash = web3.eth.send_raw_transaction(signed_transaction.rawTransaction)
    receipt = web3.eth.wait_for_transaction_receipt(transaction_hash);
    return receipt

def read_file(path):
    """Read file contents"""
    with open(path, "r") as file:
        return file.read()