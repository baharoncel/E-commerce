import os
import sys
import django

sys.path.insert(0, os.path.abspath('.'))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'marketplace_project.settings')
django.setup()

from marketplace.models import Product

print("Restoring exact real photos for all products in db.sqlite3...")

real_image_rules = [
    # Lipsticks & Glosses
    ('dewy lip booster', 'products/dewy_lip_booster_parlatici.png'),
    ('sihirli renk değiştiren ruj', 'products/seffaf_cicekli_sihirli_ruj.png'),
    ('note hydra moist', 'products/note_hydra_moist_likit_ruj.png'),
    ('farmasi', 'products/farmasi_kirmizi_likit_ruj.png'),
    ('beaulis gloss it', 'products/beaulis_gloss_it_tup_parlatici.png'),
    ('giordani gold', 'products/giordani_gold_luks_nude_ruj.png'),
    ("im'unny", 'products/imunny_kadife_mat_kirmizi_ruj.png'),
    ('golden rose velvet matte', 'products/golden_rose_velvet_matte_bordo.png'),
    ('pure nude islak', 'products/pure_nude_islak_pembe_ruj.png'),
    ('ysl rouge volupté', 'products/ysl_rouge_volupte_shine_ruj.png'),

    # Eyeshadow Palettes
    ('rose cosmetic blossom 8', 'products/eyeshadow_rose_blossom_8color.png'),
    ('pink & berry 15', 'products/eyeshadow_pink_berry_15color.png'),
    ('revolution maxi reloaded 45', 'products/eyeshadow_revolution_45color.png'),
    ('flormar sunset 10', 'products/eyeshadow_flormar_sunset_10color.png'),
    ('naked rose gold 12', 'products/eyeshadow_naked_style_12color.png'),

    # Men's Jewelry
    ('gurmet zincir kolye ve bileklik', 'products/erkek_gurmet_zincir_kolye_bileklik_set.png'),
    ('oksitli gümüş işlemeli örgü', 'products/oksitli_gumus_orgu_erkek_bileklik.png'),
    ('timsah logolu', 'products/timsah_logolu_celik_baklali_erkek_bileklik.png'),
    ('doğal lav taşı', 'products/dogal_lav_tasi_rose_gold_celik_bileklik.png'),
    ('antik yunan motifli', 'products/yunan_motifli_agir_celik_kunye_bileklik.png'),

    # Hair Accessories
    ('deniz yıldızı ve inci detaylı plaj saç zinciri', 'products/user_hair_starfish_chain.png'),
    ('gelin kristal taşlı yaprak motifli lüks yan saç tokası', 'products/user_hair_silver_leaf_comb.png'),
    ('bohem kristal taşlı alınlık & saç zinciri taç', 'products/user_hair_boho_forehead_chain.png'),
    ('altın yaprak ve inci motifli yan saç tarağı & tokası', 'products/user_hair_gold_leaf_branch.png'),
    ('incili ve kristal taşlı lüks gelin', 'products/hair_accessory_pearl_comb_real.jpg'),
    ('kadife fiyonklu', 'products/head_accessory_hairband.png'),
    ('ipek desenli baş örtüsü', 'products/head_accessory_bandana.png'),
    ('sedef görünümlü mandal', 'products/head_accessory_clip.png'),
    ('yün dokulu soft bej', 'products/head_accessory_beanie.png'),

    # Sunglasses & Watches
    ('polarize siyah kemik', 'products/accessory_sunglasses_wayfarer_real.png'),
    ('damla havacı gözlüğü', 'products/accessory_sunglasses_aviator_real.png'),
    ('retro kahverengi cat-eye', 'products/accessory_sunglasses_cateye_real.png'),
    ('aynalı cam aerodinamik spor güneş gözlüğü', 'products/accessory_sunglasses_sport_real.png'),
    ('paslanmaz çelik kordon lüks erkek kol saati', 'products/accessory_watch_silver_steel_real.png'),
    ('hakiki kahverengi deri kordon klasik erkek saat', 'products/accessory_watch_brown_leather_real.png'),
    ('rose gold ince hasır çelik kadın kol saati', 'products/accessory_watch_rose_gold_real.png'),
    ('dokunmatik ekran siyah akıllı spor saat', 'products/accessory_watch_smartwatch_real.png'),

    # Shoes & Bags
    ('siyah oxford kundura', 'products/classic_shoes_black_leather_real.jpg'),
    ('tokalı loafer', 'products/classic_shoes_brown_loafer_real.jpg'),
    ('kırmızı süet klasik topuklu stiletto', 'products/classic_shoes_red_heels_real.jpg'),
    ('monk strap', 'products/classic_shoes_navy_monk_real.jpg'),
    ('bej taba deri klasik babet', 'products/classic_shoes_beige_babet_real.jpg'),
    ('siyah deri şal detaylı klasik omuz', 'products/bag_shoulder_black_classic_scarf.png'),
    ('bej hakiki deri ikili omuz çanta set', 'products/bag_shoulder_beige_set.png'),
    ('yarım ay model siyah', 'products/bag_shoulder_half_moon.png'),
    ('ergonomik laptop & seyahat sırt çantası', 'products/bag_backpack_tech.png'),
    ('siyah deri şehir stil kadın sırt çantası', 'products/bag_shoulder_leather.png'),
    ('çok bölmeli erkek cüzdanı', 'products/accessory_wallet_leather.png'),
    ('zarf model fermuarlı kadın deri cüzdan', 'products/accessory_wallet_leather.png'),

    # Skincare, Haircare, Perfume, Oralcare
    ('dermokozmetik komple bakım seti', 'products/skincare_dermocosmetic_set.png'),
    ('the purest solutions', 'products/skincare_purest_serum_set.png'),
    ('prima botanical', 'products/skincare_prima_organic_set.png'),
    ('caudalie paris', 'products/skincare_caudalie_sun_set.png'),
    ('yves rocher pure menthe', 'products/skincare_yves_rocher_pure_menthe.png'),
    ('elseve dream long', 'products/haircare_elseve_dream_long.png'),
    ('pantene miracle rescue', 'products/haircare_pantene_miracle_rescue.png'),
    ('urban care biotin', 'products/haircare_urban_care_biotin.png'),
    ('gliss serum deep repair', 'products/haircare_gliss_deep_repair.png'),
    ('elidor anında onarıcı', 'products/haircare_elidor_repair_spray.png'),
    ('rabanne 1 million', 'products/perfume_rabanne_1million_deo.png'),
    ('bleu de chanel', 'products/perfume_bleu_de_chanel_deo.png'),
    ('gabrielle chanel', 'products/perfume_gabrielle_chanel_deo.png'),
    ('loris k-120', 'products/perfume_loris_k120_set.png'),
    ('rbl black', 'products/perfume_rbl_black_set.png'),
    ('listerine cool mint', 'products/oralcare_listerine_coolmint.png'),
    ('bambu diş fırçası', 'products/oralcare_bamboo_tongue_set.png'),
    ('alujain organik', 'products/oralcare_alujain_miswak_set.png'),
    ('biolaturca', 'products/oralcare_biolaturca_natural.png'),
    ('dentasave', 'products/oralcare_dentasave_zinc.png'),

    # Clothing & Baby
    ('mavi i̇talyan slim fit', 'products/shirt_blue_suit_real.png'),
    ('mavi italyan slim fit', 'products/shirt_blue_suit_real.png'),
    ('çizgili klasik pamuklu erkek gömlek', 'products/shirt_striped_white_real.png'),
    ('oxford beyaz erkek gömlek', 'products/shirt_white_close_real.png'),
    ('sarı desenli casual gömlek', 'products/shirt_yellow_jeans_real.png'),
    ('bej keten gömlek', 'products/shirt_white_beige_real.png'),
    ('zümrüt yeşili saten', 'products/dress_emerald_satin.png'),
    ('siyah kadife gece', 'products/dress_black_velvet.png'),
    ('leopar desenli', 'products/skirt_leopard.png'),
    ('siyah deri şişme', 'products/coat_leather_puffer.png'),
    ('kahverengi aviator', 'products/coat_aviator_brown.png'),
    ('turkuaz dökümlü bluz', 'products/blouse_turquoise.png'),
    ('kahverengi degaje bluz', 'products/blouse_brown_cowl.png'),
    ('mom fit açık mavi', 'products/jean_mom_fit_light.png'),
    ('ispanyol paça', 'products/jean_flare_blue.png'),
    ('haki keten yelek', 'products/vest_khaki_linen.png'),
    ('siyah denim salopet', 'products/jumpsuit_black_denim.png'),
    ('mavi bebek body', 'products/baby_clothing_body_blue.png'),
    ('beyaz bebek body', 'products/baby_clothing_body_white.png'),
    ('romper tulum', 'products/baby_clothing_romper.png'),
    ('bebek eşofman altı', 'products/baby_clothing_pants.png'),
    ('bebek nemlendirici', 'products/baby_moisturizer_cream.png'),
]

updated_count = 0
for p in Product.objects.all():
    title_lower = p.title.lower()
    matched = False
    for kw, img_path in real_image_rules:
        if kw in title_lower:
            p.image = img_path
            p.save()
            matched = True
            updated_count += 1
            print(f"Updated Product ID {p.id}: {p.title} -> {img_path}")
            break

print(f"\nSuccessfully restored exact real photos for {updated_count} products!")
