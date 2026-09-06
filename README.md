# Face Blockchain Verifier

An end-to-end OSINT and integrity pipeline that ingests facial images, discovers matching online identities and visual sources across the web via Google Lens/SerpApi, and anchors cryptographic identity proofs (SHA-256 digests and source URLs) immutably on the Ethereum Sepolia testnet.

---

## Features

- **Face Detection & Normalization**: Extracts face regions and computes localized spatial feature vectors.
- **Web & Social Intelligence**: Automates image-based reverse search across web platforms using SerpApi.
- **On-Chain Attestation**: Writes verification hashes and source URLs directly to a deployed Sepolia smart contract.
- **Public Auditability**: Cryptographic records are queryable on-chain via Sepolia Etherscan.

---

## Project Structure

```text
.
├── main.py                         # Runs the complete verification pipeline
├── deploy.py                       # Compiles and deploys VerificationRegistry
├── biometric_matcher.py            # Local biometric comparison helpers
├── gallery_matcher.py              # Gallery matching helpers
├── contract_abi.json               # Generated contract ABI
├── contracts/
│   └── VerificationRegistry.sol    # Solidity verification registry
├── src/
│   ├── blockchain_verifier.py      # Sepolia read/write integration
│   ├── face_detector.py            # Face detection and cropping
│   └── web_search.py               # SerpApi / Google Lens integration
├── gallery/                        # Optional local image gallery
└── haarcascade_frontalface_default.xml
```

## Requirements

- Python 3.10 or newer
- A SerpApi account and API key
- An Ethereum Sepolia RPC endpoint
- A funded Sepolia wallet for transaction fees
- `solc` 0.8.20 (installed automatically by `deploy.py` through `py-solc-x`)

## Installation

```powershell
git clone https://github.com/prathu21-gif/face-blockchain-verifier.git
cd face-blockchain-verifier

python -m venv venv
.\venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
```

## Configuration

Create a `.env` file in the project root. Start from `.env.example` and replace every placeholder with your own values:

```dotenv
SERPAPI_API_KEY=your_serpapi_key
SEPOLIA_RPC_URL=https://ethereum-sepolia-rpc.publicnode.com
PRIVATE_KEY=your_wallet_private_key
CONTRACT_ADDRESS=0xYourDeployedContractAddress
```

Never commit `.env`, private keys, or API keys. The included `.gitignore` excludes `.env` from Git.

## Deploy the Contract

To compile and deploy a new registry to Sepolia:

```powershell
python deploy.py
```

Copy the printed contract address into `CONTRACT_ADDRESS` in `.env`. The deployment script also refreshes `contract_abi.json`.

## Run Verification

Pass an image path to the pipeline:

```powershell
python main.py .\sample_input.jpg
```

The pipeline detects and crops a face, submits the crop to SerpApi for visual matches, calculates the original image's SHA-256 digest, records the primary source URL on-chain, and checks the resulting record.

Generated face crops are written as `detected_face.jpg` and are ignored by Git.

## Smart Contract

`VerificationRegistry` stores a content hash, source URL, timestamp, and submitting wallet address. Records can be inspected publicly through a Sepolia block explorer using the deployed contract address:

```text
https://sepolia.etherscan.io/address/<CONTRACT_ADDRESS>
```

This project provides technical provenance and a tamper-evident record. A visual match or source URL is not, by itself, proof of a person's identity. Use only images and data you are authorized to process, and follow applicable privacy, biometric-data, and platform policies.

## Troubleshooting

- **`SERPAPI_API_KEY is missing`**: Confirm `.env` is in the project root and contains a valid key.
- **Transaction failures**: Confirm the wallet has Sepolia ETH, the RPC endpoint is reachable, and the contract address is correct.
- **No visual matches**: Google Lens may not index the image; the pipeline creates a fallback attestation source.
- **No face detected**: Use a clear, front-facing image with sufficient lighting and resolution.

## License

No license has been specified yet.