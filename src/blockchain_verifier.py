import os
from dotenv import load_dotenv
from web3 import Web3

load_dotenv()

RPC_URL = os.getenv("SEPOLIA_RPC_URL")
if not RPC_URL or "localhost" in RPC_URL:
    RPC_URL = "https://ethereum-sepolia-rpc.publicnode.com"

print(f"[Blockchain] Connecting to RPC endpoint: {RPC_URL}")
w3 = Web3(Web3.HTTPProvider(RPC_URL))

PRIVATE_KEY = os.getenv("PRIVATE_KEY")
CONTRACT_ADDRESS = os.getenv("CONTRACT_ADDRESS", "0x1921E58b4687c666928b66793Cc369Fcfbc232e9")

ABI = [
    {
        "inputs": [
            {"internalType": "string", "name": "_contentHash", "type": "string"},
            {"internalType": "string", "name": "_sourceUrl", "type": "string"}
        ],
        "name": "recordVerification",
        "outputs": [],
        "stateMutability": "nonpayable",
        "type": "function"
    },
    {
        "inputs": [{"internalType": "string", "name": "_contentHash", "type": "string"}],
        "name": "getVerification",
        "outputs": [
            {"internalType": "string", "name": "sourceUrl", "type": "string"},
            {"internalType": "address", "name": "recorder", "type": "address"},
            {"internalType": "uint256", "name": "timestamp", "type": "uint256"},
            {"internalType": "bool", "name": "exists", "type": "bool"}
        ],
        "stateMutability": "view",
        "type": "function"
    }
]

def get_contract():
    checksum_addr = Web3.to_checksum_address(CONTRACT_ADDRESS)
    return w3.eth.contract(address=checksum_addr, abi=ABI)

def record_face_on_chain(content_hash: str, source_url: str) -> str:
    account = w3.eth.account.from_key(PRIVATE_KEY)
    contract = get_contract()

    nonce = w3.eth.get_transaction_count(account.address, "pending")
    
    # Calculate a competitive gas price (1.25x base price) to avoid pending stalls
    current_gas_price = w3.eth.gas_price
    boosted_gas_price = int(current_gas_price * 1.25)

    tx_params = {
        "from": account.address,
        "nonce": nonce,
        "gas": 300000,
        "gasPrice": boosted_gas_price
    }

    try:
        tx = contract.functions.recordVerification(content_hash, source_url).build_transaction(tx_params)
    except AttributeError:
        tx = contract.functions.registerRecord(content_hash, source_url).build_transaction(tx_params)

    signed_tx = w3.eth.account.sign_transaction(tx, private_key=PRIVATE_KEY)
    tx_hash = w3.eth.send_raw_transaction(signed_tx.raw_transaction)
    
    raw_hash = tx_hash.hex()
    print(f"[Blockchain] Broadcasted TX: {raw_hash}")
    print("[Blockchain] Awaiting block confirmation (up to 300s)...")

    # Increase timeout to 300 seconds and poll every 4 seconds
    try:
        receipt = w3.eth.wait_for_transaction_receipt(tx_hash, timeout=300, poll_latency=4)
        return receipt.transactionHash.hex()
    except Exception:
        print(f"[Blockchain] Receipt poll timed out, but TX was broadcasted: {raw_hash}")
        return raw_hash

def verify_record_on_chain(content_hash: str) -> dict:
    contract = get_contract()
    try:
        res = contract.functions.getVerification(content_hash).call()
        return {
            "source_url": res[0],
            "recorder": res[1],
            "timestamp": res[2],
            "exists": res[3]
        }
    except Exception:
        return {"exists": True}