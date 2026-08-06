import os
import urllib.request

def download_and_verify():
    artifact_dir = r"C:\Users\Bahar\.gemini\antigravity-ide\brain\3043092d-4f68-4858-be6d-1d00232fb4dc"
    media_dir = r"c:\Users\Bahar\Desktop\E-commerce\media\products"

    # Specific curated Unsplash direct photography IDs for exact hair accessories
    # 1. Hair Comb / Pearl Tiara
    url1 = "https://images.unsplash.com/photo-1590541822186-b4ac666e133c?auto=format&fit=crop&w=800&h=800&q=80"
    # Alternative direct photo URL for bridal hair comb / pin
    url1_alt = "https://images.unsplash.com/photo-1535585209827-a15fcdbc4c2d?auto=format&fit=crop&w=800&h=800&q=80"

    # 2. Scrunchies / Silk Hair Ties
    url2 = "https://images.unsplash.com/photo-1620799140408-edc6dcb6d633?auto=format&fit=crop&w=800&h=800&q=80"
    
    # 3. Gold Hair Pin / Stick
    url3 = "https://images.unsplash.com/photo-1596944924616-7b38e7cfac36?auto=format&fit=crop&w=800&h=800&q=80"

    # 4. Crystal Hair Clips / Barrettes
    url4 = "https://images.unsplash.com/photo-1576053139778-7e32f2ae3cfd?auto=format&fit=crop&w=800&h=800&q=80"

    # 5. Bow Hair Clip / Ribbon
    url5 = "https://images.unsplash.com/photo-1516914943479-89db7d9ae7f2?auto=format&fit=crop&w=800&h=800&q=80"

    candidates = [
        ("preview_1_tarak_toka.jpg", url1_alt, "1. İnci ve Kristal Yaprak Detaylı Saç Tarak Tokası"),
        ("preview_2_ipek_scrunchie.jpg", url2, "2. 3'lü %100 İpek Saten Lüks Scrunchie Saç Lastiği Seti"),
        ("preview_3_altin_hairpin.jpg", url3, "3. Minimalist Altın Metal Topuz Saç Çubuğu"),
        ("preview_4_kristal_klips.jpg", url4, "4. 4'lü Kristal Taşlı Lüks Yan Saç Klipsi Seti"),
        ("preview_5_tulle_bow.jpg", url5, "5. Krem Organze Tül Fiyonklu Romantik Saç Klipsi")
    ]

    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}

    for filename, url, title in candidates:
        art_path = os.path.join(artifact_dir, filename)
        med_path = os.path.join(media_dir, filename)
        try:
            req = urllib.request.Request(url, headers=headers)
            with urllib.request.urlopen(req) as resp, open(art_path, 'wb') as out_file:
                content = resp.read()
                out_file.write(content)
                with open(med_path, 'wb') as out_med:
                    out_med.write(content)
            print(f"Saved {filename}: {len(content)} bytes")
        except Exception as e:
            print(f"Error {filename}: {e}")

if __name__ == '__main__':
    download_and_verify()
