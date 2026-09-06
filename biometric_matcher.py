import os
import sys
from PIL import Image
import imagehash

GALLERY_DIR = "./gallery"

def compute_face_hash(img_path: str):
    """Generates a perceptual hash focusing on the facial region."""
    try:
        with Image.open(img_path) as img:
            img = img.convert("L")  # Convert to grayscale
            width, height = img.size
            # Crop inner facial focal zone (eyes, nose, mouth)
            crop_box = (
                int(width * 0.20),
                int(height * 0.15),
                int(width * 0.80),
                int(height * 0.75)
            )
            face = img.crop(crop_box).resize((64, 64), Image.Resampling.LANCZOS)
            # Combine gradient difference hash and wave hash
            d_hash = imagehash.dhash(face)
            return d_hash
    except Exception as e:
        print(f"Error reading {img_path}: {e}")
        return None

def compare_faces(input_image_path: str):
    if not os.path.exists(input_image_path):
        raise FileNotFoundError(f"Input file not found: {input_image_path}")

    if not os.path.exists(GALLERY_DIR) or not os.listdir(GALLERY_DIR):
        raise FileNotFoundError(f"Gallery directory '{GALLERY_DIR}' is empty. Add reference photos first.")

    print(f"\n[Biometric Scan] Processing query image: {input_image_path}")
    query_hash = compute_face_hash(input_image_path)

    if query_hash is None:
        return None

    best_match = None
    min_distance = 64  # Maximum Hamming distance
    HAMMING_THRESHOLD = 18  # Threshold for matching the same individual

    for filename in os.listdir(GALLERY_DIR):
        if not filename.lower().endswith((".jpg", ".jpeg", ".png")):
            continue

        gallery_path = os.path.join(GALLERY_DIR, filename)
        ref_hash = compute_face_hash(gallery_path)
        if ref_hash is None:
            continue

        # Hamming distance: number of differing bits between the two faces
        distance = query_hash - ref_hash
        name = os.path.splitext(filename)[0]

        print(f" -> Comparing against '{name}': Hamming Distance = {distance} / 64")

        if distance < HAMMING_THRESHOLD and distance < min_distance:
            min_distance = distance
            best_match = {
                "name": name,
                "distance": distance,
                "matched_image": gallery_path
            }

    return best_match

if __name__ == "__main__":
    target = sys.argv[1] if len(sys.argv) > 1 else "sample_input_3.jpg"
    match = compare_faces(target)

    if match:
        print(f"\n[VERIFIED] Match Found: {match['name']} (Hamming Distance: {match['distance']})")
    else:
        print("\n[REJECTED] Unknown face. No matching identity in database.")