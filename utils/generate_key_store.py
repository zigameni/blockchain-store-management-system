# from eth_account import Account
# private_key = "0xb64be88dd6b89facf295f4fd0dda082efcbe95a2bb4478f5ee582b7efe88cf60"
# account = Account.from_key(private_key)
# keystore = Account.encrypt(private_key, 'iepblockchain')
# print(keystore)


import bcrypt

def hash_password(password):
    """Hash a password using bcrypt"""
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

def verify_password(password, hashed_password):
    """Verify password against hashed password"""
    return bcrypt.checkpw(password.encode('utf-8'), hashed_password.encode('utf-8'))

password = "evenmoremoney"
hashed_password = hash_password(password)
print(hashed_password)

print('\n')
print(verify_password(password, hashed_password))