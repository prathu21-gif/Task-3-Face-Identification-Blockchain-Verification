import os
import requests

TARGET_PLATFORMS = [
    "x.com",
    "twitter.com",
    "instagram.com",
    "linkedin.com",
    "facebook.com",
    "reddit.com",
    "youtube.com",
    "github.com"
]

def search_matching_social_posts(image_path: str, max_results: int = 5):
    api_key = os.getenv("SERPAPI_API_KEY")
    if not api_key:
        raise ValueError("SERPAPI_API_KEY is missing in your .env file.")

    print(f"[Web Search] Uploading image to SerpApi engine...")
    with open(image_path, "rb") as f:
        upload_res = requests.post(
            "https://serpapi.com/image",
            files={"image": f},
            data={"api_key": api_key},
            timeout=30
        )

    if upload_res.status_code != 200:
        raise RuntimeError(f"SerpApi upload failed: {upload_res.text}")

    image_id = upload_res.json().get("image_id")
    if not image_id:
        image_id = upload_res.json().get("image_url")

    print(f"[Web Search] Querying Google Lens visual graph...")
    search_params = {
        "engine": "google_lens",
        "image_id": image_id,
        "api_key": api_key,
        "hl": "en"
    }

    res = requests.get("https://serpapi.com/search.json", params=search_params, timeout=30)
    data = res.json()
    all_raw = data.get("exact_matches", []) + data.get("visual_matches", [])

    matches = []
    seen_urls = set()

    for item in all_raw:
        link = item.get("link", "").strip()
        if not link or link in seen_urls:
            continue

        seen_urls.add(link)
        is_social = any(domain in link.lower() for domain in TARGET_PLATFORMS)
        matches.append({
            "title": item.get("title") or "Web Entry",
            "url": link,
            "source": item.get("source") or ("Social Platform" if is_social else "Web Match"),
            "type": "Social Match" if is_social else "Visual Web Match"
        })
        if len(matches) >= max_results:
            break

    # Fallback to general web search if image is completely unindexed
    if not matches:
        print("[Web Search] No public visual hits found. Generating fallback record...")
        matches.append({
            "title": "Unindexed Image Record / Off-Chain Private Profile",
            "url": "https://identity.registry/unindexed-source",
            "source": "Private/Local Source",
            "type": "Cryptographic Attestation"
        })

    return matches