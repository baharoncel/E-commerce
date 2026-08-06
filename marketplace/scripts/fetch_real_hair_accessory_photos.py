import os
import urllib.request

def fetch_photos():
    artifact_dir = r"C:\Users\Bahar\.gemini\antigravity-ide\brain\3043092d-4f68-4858-be6d-1d00232fb4dc"
    media_dir = r"c:\Users\Bahar\Desktop\E-commerce\media\products"
    os.makedirs(artifact_dir, exist_ok=True)
    os.makedirs(media_dir, exist_ok=True)

    # Curated real e-commerce camera photography URLs for hair accessories
    photo_sources = [
        {
            "name": "photo_1_pearl_comb.jpg",
            "url": "https://images.unsplash.com/photo-1596944924616-7b38e7cfac36?auto=format&fit=crop&w=800&h=800&q=80",
            "title": "1. İncili ve Kristal Taşlı Saç Tarak Tokası"
        },
        {
            "name": "photo_2_satin_scrunchies.jpg",
            "url": "https://images.unsplash.com/photo-1606107557195-0e29a4b5b4aa?auto=format&fit=crop&w=800&h=800&q=80",
            "title": "2. 3'lü İpek Saten Scrunchie Saç Lastiği Seti"
        },
        {
            "name": "photo_3_gold_hairpin.jpg",
            "url": "https://images.unsplash.com/photo-1605100804763-247f67b3557e?auto=format&fit=crop&w=800&h=800&q=80",
            "title": "3. Minimalist Altın Metal Topuz Saç Çubuğu"
        },
        {
            "name": "photo_4_crystal_clips.jpg",
            "url": "https://images.unsplash.com/photo-1620799140408-edc6dcb6d633?auto=format&fit=crop&w=800&h=800&q=80",
            "title": "4. 4'lü Kristal Taşlı Lüks Yan Saç Klipsi Seti"
        },
        {
            "name": "photo_5_organza_bow.jpg",
            "url": "https://images.unsplash.com/photo-1576053139778-7e32f2ae3cfd?auto=format&fit=crop&w=800&h=800&q=80",
            "title": "5. Krem Organze Tül Fiyonklu Saç Tokası Klipsi"
        }
    ]

    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}

    for item in photo_sources:
        art_path = os.path.join(artifact_dir, item["name"])
        med_path = os.path.join(media_dir, item["name"])
        try:
            req = urllib.request.Request(item["url"], headers=headers)
            with urllib.request.urlopen(req) as resp, open(art_path, 'wb') as out_file:
                content = resp.read()
                out_file.write(content)
                with open(med_path, 'wb') as out_med:
                    out_med.write(content)
            print(f"Successfully downloaded: {item['name']} ({len(content)} bytes)")
        except Exception as e:
            print(f"Error downloading {item['name']}: {e}")

if __name__ == '__main__':
    fetch_photos()
