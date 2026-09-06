import sys
import hashlib
from src.face_detector import detect_and_crop_face
from src.web_search import search_matching_social_posts
from src.blockchain_verifier import record_face_on_chain, verify_record_on_chain

def calculate_sha256(file_path: str) -> str:
    sha = hashlib.sha256()
    with open(file_path, "rb") as f:
        while chunk := f.read(8192):
            sha.update(chunk)
    return sha.hexdigest()

def run_pipeline(image_path: str):
    print("\n" + "=" * 55)
    print("      FACE IDENTIFICATION & BLOCKCHAIN REGISTRY")
    print("=" * 55)

    # Step 1: Crop Face Area
    print(f"\n[1/3] Step 1: Ingesting Face Scan -> {image_path}")
    face_meta = detect_and_crop_face(image_path)

    # Step 2: Live Multi-Link Web/Social Search
    print("\n[2/3] Step 2: Searching Web/Social Media via Google Lens...")
    matches = search_matching_social_posts(face_meta["crop_path"], max_results=5)

    print(f"\nDiscovered {len(matches)} Relevant Matching Source(s):")
    print("-" * 55)
    for idx, match in enumerate(matches, 1):
        print(f"[{idx}] Type:     {match['type']} ({match['source']})")
        print(f"    Title:    {match['title']}")
        print(f"    URL:      {match['url']}")
        print("-" * 55)

    primary_match = matches[0]

    # Step 3: Hash and Commit Primary Canonical Proof to Sepolia
    print("\n[3/3] Step 3: Hashing & Committing to Blockchain...")
    image_hash = calculate_sha256(image_path)
    print(f" SHA-256 Fingerprint: {image_hash}")

    tx_hash = record_face_on_chain(image_hash, primary_match["url"])
    print(f" Confirmed Transaction Hash: {tx_hash}")

    # Step 4: Verify
    on_chain = verify_record_on_chain(image_hash)
    print(f"\nSTATUS: {'CONFIRMED ON-CHAIN' if on_chain['exists'] else 'FAILED'}")
    print("=" * 55 + "\n")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python main.py <path_to_image>")
        sys.exit(1)
    run_pipeline(sys.argv[1])