import os
import re
from bs4 import BeautifulSoup

instagram_path = os.path.expanduser("~/Downloads/instagram-alihankusakli-2026-05-01-Li4SOAFL")

files = [
    "your_instagram_activity/media/posts_1.html",
    "your_instagram_activity/media/stories.html",
    "your_instagram_activity/media/reels.html",
    "your_instagram_activity/media/igtv_videos.html",
]

all_captions = []

for file in files:
    filepath = os.path.join(instagram_path, file)
    if not os.path.exists(filepath):
        print(f"Not found: {filepath}")
        continue

    with open(filepath, "r", encoding="utf-8") as f:
        soup = BeautifulSoup(f, "html.parser")

    for div in soup.find_all("div"):
        text = div.get_text(strip=True)

        # Temel filtreler
        if len(text) < 50:
            continue
        if "Enlem" in text or "Boylam" in text:
            continue
        if "Kamera Meta" in text:
            continue
        if "Görüntü için" in text:
            continue
        if "Etiketlendi" in text:
            continue
        if "Music" in text or "Rap" in text or "Hip Hop" in text:
            continue

        # Hashtag'leri temizle
        text = re.sub(r'#\w+', '', text)

        # Tarihleri temizle (örn: "Nis 11, 2025 6:13 am")
        text = re.sub(r'[A-ZÇĞİÖŞÜa-zçğışöüA-Z]{3}\s\d{2},\s\d{4}.*', '', text)

        # Fazla boşlukları temizle
        text = re.sub(r'\s+', ' ', text).strip()

        if len(text) < 50:
            continue

        all_captions.append(text)

all_captions = list(dict.fromkeys(all_captions))

print(f"Total captions found: {len(all_captions)}")

with open("data/instagram.txt", "w", encoding="utf-8") as f:
    f.write("\n\n".join(all_captions))

print("Saved to data/instagram.txt")