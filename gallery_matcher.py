import os
import json
import numpy as np
from PIL import Image

GALLERY_DIR = "./gallery"
METADATA_FILE = os.path.join(GALLERY_DIR, "profiles.json")

def extract_face_vector(image_path: str, grid_size=(16, 16)) -> np.ndarray:
    """Extracts a normalized 256-dimensional spatial gradient vector of the face."""
    with Image.open(image_path) as img:
        img = img.convert("L")  # Grayscale
        width, height = img.size
        
        # Center-crop face bounding box
        face_crop = img.crop((
            int(width * 0.20),
            int(height * 0.15),
            int(width * 0.80),
            int(height * 0.75)
        ))
        
        resized = face_crop.resize(grid_size, Image.Resampling.LANCZOS)
        arr = np.asarray(resized, dtype=np.float32)
        
        # Compute horizontal and vertical gradients
        gx, gy = np.gradient(arr)
        feature_vector = np.concatenate([gx.flatten(), gy.flatten()])
        
        # L2-normalize vector
        norm = np.linalg.norm(feature_vector)
        return feature_vector / (norm + 1e-7)

def match_against_gallery(input_image_path: str, threshold: float = 0.70):
    """Compares query face against enrolled gallery profiles."""
    if not os.path.exists(METADATA_FILE):
        raise FileNotFoundError(f"Missing '{METADATA_FILE}'. Enroll at least one profile first.")

    with open(METADATA_FILE, "r") as f:
        registry = json.load(f)

    query_vec = extract_face_vector(input_image_path)
    best_match = None
    max_sim = -1.0

    print(f"\n[Gallery Matcher] Matching {input_image_path} against enrolled profiles...")

    for profile in registry:
        ref_path = os.path.join(GALLERY_DIR, profile["image_filename"])
        if not os.path.exists(ref_path):
            continue

        ref_vec = extract_face_vector(ref_path)
        # Cosine similarity (dot product of normalized vectors)
        sim = float(np.dot(query_vec, ref_vec))
        print(f" -> Comparing with {profile['name']}: Similarity = {sim:.4f}")

        if sim > max_sim:
            max_sim = sim
            best_match = profile

    if max_sim >= threshold and best_match:
        return {
            "name": best_match["name"],
            "url": best_match["profile_url"],
            "similarity": max_sim,
            "title": f"Verified Identity: {best_match['name']}"
        }

    return None