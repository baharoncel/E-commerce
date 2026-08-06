import os
import urllib.request

def fetch_real_mens_photos():
    artifact_dir = r"C:\Users\Bahar\.gemini\antigravity-ide\brain\3043092d-4f68-4858-be6d-1d00232fb4dc"
    media_dir = r"c:\Users\Bahar\Desktop\E-commerce\media\products"

    # Curated authentic men's jewelry photo URLs
    # 1. Men's Ring: Real camera photo of men's steel signet ring
    url_ring = "https://images.unsplash.com/photo-1622398925373-3f91b1e275f5?auto=format&fit=crop&w=800&h=800&q=80" # Men's ring
    url_ring_alt = "https://images.unsplash.com/photo-1598560917505-59a3ad559071?auto=format&fit=crop&w=800&h=800&q=80" # Men's ring

    # 2. Men's Leather Bracelet: Real camera photo of braided black leather bracelet
    url_bracelet = "https://images.unsplash.com/photo-1611591475168-a28a301416e7?auto=format&fit=crop&w=800&h=800&q=80"
    url_bracelet_alt = "https://images.unsplash.com/photo-1573408301185-9146fe634ad0?auto=format&fit=crop&w=800&h=800&q=80"

    # 3. Men's Necklace: Real camera photo of men's steel chain necklace
    url_necklace = "https://images.unsplash.com/photo-1599643478518-a784e5dc4c8f?auto=format&fit=crop&w=800&h=800&q=80"

    # 4. Men's Earrings: Real camera photo of men's black steel hoop/stud earrings
    url_earrings = "https://images.unsplash.com/photo-1630019852942-f89202989a59?auto=format&fit=crop&w=800&h=800&q=80"
    url_earrings_alt = "https://images.unsplash.com/photo-1535632066927-ab7c9ab60908?auto=format&fit=crop&w=800&h=800&q=80"

    # 5. Men's Cufflinks: Real camera photo of men's cufflinks
    url_cufflinks = "https://images.unsplash.com/photo-1617038260897-41a1f14a8ca0?auto=format&fit=crop&w=800&h=800&q=80"

    candidates = [
        ("real_photo_mens_ring.jpg", [url_ring, url_ring_alt]),
        ("real_photo_mens_bracelet.jpg", [url_bracelet_alt, url_bracelet]),
        ("real_photo_mens_necklace.jpg", [url_necklace]),
        ("real_photo_mens_earrings.jpg", [url_earrings, url_earrings_alt]),
        ("real_photo_mens_cufflinks.jpg", [url_cufflinks])
    ]

    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}

    for filename, urls in candidates:
        art_path = os.path.join(artifact_dir, filename)
        med_path = os.path.join(media_dir, filename)
        success = False
        for url in urls:
            try:
                req = urllib.request.Request(url, headers=headers)
                with urllib.request.urlopen(req) as resp, open(art_path, 'wb') as out_file:
                    content = resp.read()
                    out_file.write(content)
                    with open(med_path, 'wb') as out_med:
                        out_med.write(content)
                print(f"Downloaded {filename} ({len(content)} bytes) from {url}")
                success = True
                break
            except Exception as e:
                print(f"Error {filename} from {url}: {e}")

if __name__ == '__main__':
    fetch_real_mens_photos()
