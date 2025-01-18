from PIL import Image
import os

# Path to your original image
original_image_path = "icon-500.png"
output_directory = "icons/"
sizes = [16, 32, 48, 128]

# Ensure the output directory exists
os.makedirs(output_directory, exist_ok=True)

try:
    # Open the original image
    with Image.open(original_image_path) as img:
        for size in sizes:
            # Resize the image
            resized_img = img.resize((size, size), Image.Resampling.LANCZOS)  # Use Resampling if available
            resized_img.save(f"{output_directory}icon-{size}.png")
            print(f"Saved resized image: icon-{size}.png")
except AttributeError:
    print("Resampling not available. Falling back to LANCZOS directly.")
    with Image.open(original_image_path) as img:
        for size in sizes:
            resized_img = img.resize((size, size), Image.LANCZOS)  # Direct fallback
            resized_img.save(f"{output_directory}icon-{size}.png")
            print(f"Saved resized image: icon-{size}.png")
except FileNotFoundError:
    print(f"Error: File '{original_image_path}' not found. Ensure the path is correct.")
except Exception as e:
    print(f"Unexpected error: {e}")
