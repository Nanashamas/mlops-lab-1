from pathlib import Path
from PIL import Image
from tqdm import tqdm

CLASS_MAPPING = {
    0: "Bread",
    1: "Dairy product",
    2: "Dessert",
    3: "Egg",
    4: "Fried food",
    5: "Meat",
    6: "Noodles-Pasta",
    7: "Rice",
    8: "Seafood",
    9: "Soup",
    10: "Vegetable-Fruit",
}

SPLITS = ["training", "evaluation", "validation"]
TARGET_SIZE = (128, 128)
MINI_LIMIT = 100


def process_dataset():
    base_dir = Path("data")
    raw_dir = base_dir / "food11_raw"
    processed_dir = base_dir / "food11_processed"
    mini_dir = base_dir / "food11_processed_mini"

    if not raw_dir.exists():
        raise FileNotFoundError(f"Raw directory not found: {raw_dir.resolve()}")

    for split in SPLITS:
        raw_split = raw_dir / split
        if not raw_split.exists():
            print(f"Skipping split '{split}' (not found in {raw_split})")
            continue

        print(f"\nProcessing split: {split}")
        class_counts = {cls_id: 0 for cls_id in CLASS_MAPPING.keys()}

        image_files = sorted(
            [f for f in raw_split.iterdir() if f.suffix.lower() in [".jpg", ".jpeg", ".png"]]
        )

        for img_path in tqdm(image_files, desc=f"{split}"):
            try:
                class_id = int(img_path.name.split("_")[0])
                class_name = CLASS_MAPPING[class_id]
            except (ValueError, KeyError):
                continue

            full_out_dir = processed_dir / split / class_name
            full_out_dir.mkdir(parents=True, exist_ok=True)

            with Image.open(img_path) as img:
                img_resized = img.convert("RGB").resize(
                    TARGET_SIZE, Image.Resampling.BILINEAR
                )
                img_resized.save(full_out_dir / img_path.name, "JPEG", quality=90)

                if class_counts[class_id] < MINI_LIMIT:
                    mini_out_dir = mini_dir / split / class_name
                    mini_out_dir.mkdir(parents=True, exist_ok=True)
                    img_resized.save(mini_out_dir / img_path.name, "JPEG", quality=90)
                    class_counts[class_id] += 1


if __name__ == "__main__":
    process_dataset()