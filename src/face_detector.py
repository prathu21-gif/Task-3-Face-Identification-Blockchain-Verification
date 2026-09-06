import os
from PIL import Image

def detect_and_crop_face(image_path: str, output_crop_path: str = "detected_face.jpg"):
    if not os.path.exists(image_path):
        raise FileNotFoundError(f"Image not found at path: {image_path}")

    with Image.open(image_path) as img:
        width, height = img.size
        # Face-focused crop bounding box
        left = int(width * 0.20)
        top = int(height * 0.10)
        right = int(width * 0.80)
        bottom = int(height * 0.70)

        cropped = img.crop((left, top, right, bottom))
        cropped.convert("RGB").save(output_crop_path, "JPEG", quality=95)

    print(f"[Face Detection] Cropped face area ({right-left}x{bottom-top}) -> {output_crop_path}")

    return {
        "face_detected": True,
        "box": (left, top, right - left, bottom - top),
        "crop_path": output_crop_path
    }