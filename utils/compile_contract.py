#!/usr/bin/env python3
"""
Compile Solidity smart contract
"""
import json
from solcx import compile_source, install_solc, set_solc_version

# Install specific version
print("Installing Solidity compiler version 0.8.18...")
install_solc('0.8.18')
set_solc_version('0.8.18')

# Read contract source
print("Reading contract source...")
with open('../blockchain/contracts/OrderPayment.sol', 'r') as f:
    contract_source = f.read()

# Compile contract
print("Compiling contract...")
compiled_sol = compile_source(
    contract_source,
    output_values=['abi', 'bin']
)

# Get contract interface
contract_id, contract_interface = compiled_sol.popitem()

# Save ABI
abi = contract_interface['abi']
with open('../blockchain/output/OrderPayment.abi', 'w') as f:
    json.dump(abi, f, indent=2)
print("ABI saved to blockchain/output/OrderPayment.abi")

# Save bytecode
bytecode = contract_interface['bin']
with open('../blockchain/output/OrderPayment.bin', 'w') as f:
    f.write(bytecode)
print("Bytecode saved to blockchain/output/OrderPayment.bin")

print("\nContract compiled successfully!")
print(f"ABI length: {len(json.dumps(abi))} characters")
print(f"Bytecode length: {len(bytecode)} characters")