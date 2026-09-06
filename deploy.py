import os
import json
from dotenv import load_dotenv
from web3 import Web3
from solcx import compile_standard, install_solc

load_dotenv()

print("Installing solc compiler v0.8.20...")
install_solc("0.8.20")

with open("./contracts/VerificationRegistry.sol", "r") as file:
    contract_source = file.read()

print("Compiling smart contract...")
compiled_sol = compile_standard(
    {
        "language": "Solidity",
        "sources": {"VerificationRegistry.sol": {"content": contract_source}},
        "settings": {
            "outputSelection": {
                "*": {"*": ["abi", "metadata", "evm.bytecode", "evm.sourceMap"]}
            }
        },
    },
    solc_version="0.8.20",
)

abi = compiled_sol["contracts"]["VerificationRegistry.sol"]["VerificationRegistry"]["abi"]
bytecode = compiled_sol["contracts"]["VerificationRegistry.sol"]["VerificationRegistry"]["evm"]["bytecode"]["object"]

# Save ABI for blockchain_verifier.py
with open("contract_abi.json", "w") as f:
    json.dump(abi, f)

rpc_url = os.getenv("RPC_URL", "https://ethereum-sepolia-rpc.publicnode.com")
private_key = os.getenv("PRIVATE_KEY")

if not private_key:
    raise ValueError("PRIVATE_KEY is missing in your .env file!")

w3 = Web3(Web3.HTTPProvider(rpc_url))
account = w3.eth.account.from_key(private_key)

print(f"Deploying contract using account: {account.address}")
Registry = w3.eth.contract(abi=abi, bytecode=bytecode)
nonce = w3.eth.get_transaction_count(account.address)

tx = Registry.constructor().build_transaction({
    "chainId": w3.eth.chain_id,
    "gasPrice": w3.eth.gas_price,
    "from": account.address,
    "nonce": nonce,
})

signed_tx = w3.eth.account.sign_transaction(tx, private_key=private_key)
tx_hash = w3.eth.send_raw_transaction(signed_tx.raw_transaction)
print("Waiting for deployment transaction receipt...")
tx_receipt = w3.eth.wait_for_transaction_receipt(tx_hash)

print("\n=======================================================")
print(f"SUCCESS! Contract Deployed Address: {tx_receipt.contractAddress}")
print("Copy this address into your .env file as CONTRACT_ADDRESS")
print("=======================================================\n")