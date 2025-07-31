from pathlib import Path
from PIL import Image

# Base directories
BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"
MOBILE_DIR = DATA_DIR / "mobile"
SCALE = 0.33

def log(msg):
    print(f"[INFO] {msg}")

# Step 1: Convert all non-JPG images (background and content)
def convert_to_jpg(image_path: Path):
    try:
        with Image.open(image_path) as img:
            rgb = img.convert("RGB")
            new_path = image_path.with_suffix(".jpg")
            rgb.save(new_path, "JPEG", quality=85)
            log(f"➜ Converted to JPG: {new_path}")
        if image_path != new_path:
            image_path.unlink()
            log(f"✗ Deleted original: {image_path}")
    except Exception as e:
        log(f"✗ Failed to convert {image_path}: {e}")

# Background image conversion
original_bg = DATA_DIR / "background.png"
converted_bg = DATA_DIR / "background.jpg"
if original_bg.exists() and not converted_bg.exists():
    convert_to_jpg(original_bg)

# Convert all .jpeg/.png/.gif in subdirs
for subdir in DATA_DIR.iterdir():
    print(f"[CHECK] Found subdir: {subdir}")
    if not subdir.is_dir() or subdir.name.lower() == "mobile":
        print(f"[SKIP] Not a directory: {subdir}")
        continue
    for image_path in subdir.iterdir():
        ext = image_path.suffix.lower()
        if ext in {'.jpeg', '.png', '.gif'}:
            print(f"[CONVERT] Converting {image_path}")
            convert_to_jpg(image_path)
        elif ext == '.jpg':
            continue  # already good
        else:
            log(f"Skipped unsupported file: {image_path}")

# Step 2: Downscale background.jpg to mobile/background.jpg
background_jpg = DATA_DIR / "background.jpg"
mobile_bg = MOBILE_DIR / "background.jpg"
if background_jpg.exists() and not mobile_bg.exists():
    try:
        mobile_bg.parent.mkdir(parents=True, exist_ok=True)
        with Image.open(background_jpg) as img:
            new_size = (int(img.width * SCALE), int(img.height * SCALE))
            img_resized = img.resize(new_size, Image.LANCZOS)
            img_resized.save(mobile_bg, "JPEG", quality=85)
            log(f"➜ Created mobile background.jpg: {mobile_bg} ({new_size[0]}x{new_size[1]})")
    except Exception as e:
        log(f"✗ Failed to downscale background.jpg: {e}")
else:
    log("✓ Mobile background already exists or source missing")

# Step 3: Downscale all .jpgs in content
for subdir in DATA_DIR.iterdir():
    if not subdir.is_dir() or subdir.name.lower() == "mobile":
        continue

    for image_path in subdir.iterdir():
        if image_path.suffix.lower() != '.jpg':
            continue
        relative_path = image_path.relative_to(DATA_DIR)
        mobile_path = MOBILE_DIR / relative_path

        if mobile_path.exists():
            log(f"✓ Mobile version exists: {mobile_path}")
            continue

        try:
            mobile_path.parent.mkdir(parents=True, exist_ok=True)
            with Image.open(image_path) as img:
                new_size = (int(img.width * SCALE), int(img.height * SCALE))
                img_resized = img.resize(new_size, Image.LANCZOS)
                img_resized.save(mobile_path, "JPEG", quality=85)
                log(f"➜ Created mobile version: {mobile_path} ({new_size[0]}x{new_size[1]})")
        except Exception as e:
            log(f"✗ Failed to downscale {image_path.name}: {e}")
