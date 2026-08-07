import os
import sys
import django
import uuid
from decimal import Decimal

sys.path.insert(0, os.path.abspath('.'))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'marketplace_project.settings')
django.setup()

from marketplace.models import Category, Product, ProductVariant, SellerProfile, ProductReview

print("Starting complete organization of all categories with real product photos...")

# 1. Clean up old dummy products with generic names or missing/broken data
dummy_titles = [
    'Şık ve Kaliteli Hırka & Kazak Modeli',
    'Şık ve Kaliteli Ceket Modeli',
    'Şık ve Kaliteli Şort Modeli',
    'Şık ve Kaliteli Elbise Modeli',
    'Şık ve Rahat',
]
for p in Product.objects.all():
    if any(dt in p.title for dt in dummy_titles) or (p.image and p.image.name in ['products/tshirt_blue_plain.png', 'products/coat_black_puffer.png', 'products/shampoo.png', 'products/skincare.png'] and 'Şık' in p.title):
        print(f"Removing dummy product ID {p.id}: {p.title}")
        ProductVariant.objects.filter(product=p).delete()
        ProductReview.objects.filter(product=p).delete()
        p.delete()

# Get default sellers
seller_tekno = SellerProfile.objects.filter(user__username='tech_seller').first() or SellerProfile.objects.first()
seller_fashion = SellerProfile.objects.filter(user__username='fashion_seller').first() or SellerProfile.objects.first()

# Define Category structure
def get_cat(name, parent=None, slug=None):
    if not slug:
        slug = name.lower().replace(' ', '-').replace('&', 've').replace('ç', 'c').replace('ğ', 'g').replace('ı', 'i').replace('ö', 'o').replace('ş', 's').replace('ü', 'u')
    cat, _ = Category.objects.get_or_create(name=name, defaults={'parent': parent, 'slug': slug})
    if parent and cat.parent != parent:
        cat.parent = parent
        cat.save()
    return cat

# Main Categories
cat_giyim = get_cat('Giyim & Moda')
cat_ayakkabi = get_cat('Ayakkabı')
cat_aksesuar = get_cat('Saat & Aksesuar')
cat_taki = get_cat('Takılar')
cat_elektronik = get_cat('Elektronik & Teknoloji')
cat_bebek = get_cat('Çocuk & Bebek')
cat_kozmetik = get_cat('Kozmetik & Kişisel Bakım')

# Catalog items definition
catalog = [
    # --- GİYİM & MODA ---
    {
        'title': 'Mavi İtalyan Slim Fit Takım Elbise Gömleği',
        'desc': '%100 Pamuklu nefes alan kumaş, leke tutmaz yaka ve slim fit İtalyan kesim şık erkek gömlek.',
        'price': Decimal('549.90'),
        'image': 'products/shirt_blue_suit_real.png',
        'category': cat_giyim,
        'seller': seller_fashion,
        'variants': [('Mavi', 'S'), ('Mavi', 'M'), ('Mavi', 'L'), ('Mavi', 'XL')]
    },
    {
        'title': 'Çizgili Klasik Pamuklu Erkek Gömlek',
        'desc': 'Mavi-beyaz ince çizgili, kol manşet detaylı klasik stil günlük erkek gömlek.',
        'price': Decimal('499.00'),
        'image': 'products/shirt_striped_white_real.png',
        'category': cat_giyim,
        'seller': seller_fashion,
        'variants': [('Çizgili Mavi', 'M'), ('Çizgili Mavi', 'L'), ('Çizgili Mavi', 'XL')]
    },
    {
        'title': 'Oxford Beyaz Slim Fit Pamuk Erkek Gömlek',
        'desc': 'Zarif Oxford dokuma pamuk kumaş, düğmeli yaka ve şık slim fit beyaz gömlek.',
        'price': Decimal('529.00'),
        'image': 'products/shirt_white_close_real.png',
        'category': cat_giyim,
        'seller': seller_fashion,
        'variants': [('Beyaz', 'S'), ('Beyaz', 'M'), ('Beyaz', 'L'), ('Beyaz', 'XL')]
    },
    {
        'title': 'Sarı Desenli Casual Yazlık Erkek Gömlek',
        'desc': 'Canlı sarı renkli, rahat kesim yıkanmış pamuklu casual gömlek.',
        'price': Decimal('429.50'),
        'image': 'products/shirt_yellow_jeans_real.png',
        'category': cat_giyim,
        'seller': seller_fashion,
        'variants': [('Sarı', 'M'), ('Sarı', 'L')]
    },
    {
        'title': 'Turkuaz Dökümlü Saten Kadın Bluz',
        'desc': 'Şık turkuaz rengi saten dokulu, V yaka dökümlü zarif kadın bluz.',
        'price': Decimal('479.90'),
        'image': 'products/blouse_turquoise.png',
        'category': cat_giyim,
        'seller': seller_fashion,
        'variants': [('Turkuaz', 'S'), ('Turkuaz', 'M'), ('Turkuaz', 'L')]
    },
    {
        'title': 'Puantiyeli Viskon Şık Kadın Bluz',
        'desc': 'Siyah üzeri beyaz puantiye desenli, karpuz kol şık günlük ve ofis bluzu.',
        'price': Decimal('399.00'),
        'image': 'products/blouse_polka_dot.png',
        'category': cat_giyim,
        'seller': seller_fashion,
        'variants': [('Puantiyeli Siyah', 'S'), ('Puantiyeli Siyah', 'M')]
    },
    {
        'title': 'Kahverengi Degaje Yaka Saten Kadın Bluz',
        'desc': 'Dökümlü degaje yaka, kahverengi parlak saten kumaştan özel davet bluzu.',
        'price': Decimal('459.00'),
        'image': 'products/blouse_brown_cowl.png',
        'category': cat_giyim,
        'seller': seller_fashion,
        'variants': [('Kahverengi', 'S'), ('Kahverengi', 'M')]
    },
    {
        'title': 'Zümrüt Yeşili Saten Gece Elbisesi',
        'desc': 'Özel davet ve abiyeler için yırtmaçlı, sırt dekolteli zümrüt yeşili dökümlü saten elbise.',
        'price': Decimal('1290.00'),
        'image': 'products/dress_emerald_satin.png',
        'category': cat_giyim,
        'seller': seller_fashion,
        'variants': [('Zümrüt Yeşili', '36'), ('Zümrüt Yeşili', '38'), ('Zümrüt Yeşili', '40')]
    },
    {
        'title': 'Siyah Kadife Lüks Gece Elbisesi',
        'desc': 'Yoğun siyah kadife dokulu, vücudu saran şık gece ve parti elbisesi.',
        'price': Decimal('1150.00'),
        'image': 'products/dress_black_velvet.png',
        'category': cat_giyim,
        'seller': seller_fashion,
        'variants': [('Siyah', '36'), ('Siyah', '38')]
    },
    {
        'title': 'Leopar Desenli Saten Midi Etek',
        'desc': 'Yüksek bel, leopar desenli dökümlü saten midi kadın etek.',
        'price': Decimal('489.00'),
        'image': 'products/skirt_leopard.png',
        'category': cat_giyim,
        'seller': seller_fashion,
        'variants': [('Leopar', 'S'), ('Leopar', 'M'), ('Leopar', 'L')]
    },
    {
        'title': 'Siyah Kapüşonlu Şişme Kadın/Erkek Mont',
        'desc': 'Rüzgar ve su geçirmez dokulu, elyaf dolgulu sıcak tutan mat siyah şişme mont.',
        'price': Decimal('1499.00'),
        'image': 'products/coat_black_puffer.png',
        'category': cat_giyim,
        'seller': seller_fashion,
        'variants': [('Siyah', 'M'), ('Siyah', 'L'), ('Siyah', 'XL')]
    },
    {
        'title': 'Kahverengi Süet Kürk Yaka Aviator Ceket',
        'desc': 'İç kısmı yumuşak kürklü, hakiki görünümlü kahverengi aviator tarz ceket.',
        'price': Decimal('1690.00'),
        'image': 'products/coat_aviator_brown.png',
        'category': cat_giyim,
        'seller': seller_fashion,
        'variants': [('Kahverengi', 'M'), ('Kahverengi', 'L')]
    },
    {
        'title': 'Yüksek Bel Mom Fit Açık Mavi Jean Pantolon',
        'desc': '%100 Pamuklu kot kumaşı, yüksek bel rahat mom fit açık mavi jean.',
        'price': Decimal('589.00'),
        'image': 'products/jean_mom_fit_light.png',
        'category': cat_giyim,
        'seller': seller_fashion,
        'variants': [('Açık Mavi', '34'), ('Açık Mavi', '36'), ('Açık Mavi', '38')]
    },
    {
        'title': 'İspanyol Paça Koyu Mavi Denim Pantolon',
        'desc': 'Esnek stretch denim kumaş, paçaya doğru genişleyen ispanyol kesim kot pantolon.',
        'price': Decimal('549.00'),
        'image': 'products/jean_flare_blue.png',
        'category': cat_giyim,
        'seller': seller_fashion,
        'variants': [('Koyu Mavi', '36'), ('Koyu Mavi', '38'), ('Koyu Mavi', '40')]
    },
    {
        'title': 'Haki Keten Düğmeli Şık Yelek',
        'desc': 'Doğal keten kumaştan üretilmiş, önü düğmeli maskülen kesim haki kadın/erkek yelek.',
        'price': Decimal('429.00'),
        'image': 'products/vest_khaki_linen.png',
        'category': cat_giyim,
        'seller': seller_fashion,
        'variants': [('Haki', 'S'), ('Haki', 'M'), ('Haki', 'L')]
    },

    # --- AYAKKABI ---
    {
        'title': 'Hakiki Deri Erkek Siyah Oxford Kundura',
        'desc': '%100 Hakiki dana derisi, kösele tabanlı ve bağcıklı resmi siyah oxford ayakkabı.',
        'price': Decimal('1390.00'),
        'image': 'products/classic_shoes_black_leather_real.jpg',
        'category': cat_ayakkabi,
        'seller': seller_fashion,
        'variants': [('Siyah', '41'), ('Siyah', '42'), ('Siyah', '43'), ('Siyah', '44')]
    },
    {
        'title': 'Hakiki Deri Taba Tokalı Loafer Ayakkabı',
        'desc': 'El işçiliği taba deri, altın tokalı ve rahat tabanlı şık erkek loafer.',
        'price': Decimal('1290.00'),
        'image': 'products/classic_shoes_brown_loafer_real.jpg',
        'category': cat_ayakkabi,
        'seller': seller_fashion,
        'variants': [('Taba', '41'), ('Taba', '42'), ('Taba', '43')]
    },
    {
        'title': 'Rugan Kırmızı Topuklu Stiletto Kadın Ayakkabısı',
        'desc': '10 cm ince topuk, parlak kırmızı rugan kaplama ikonik davet stilettosu.',
        'price': Decimal('899.00'),
        'image': 'products/classic_shoes_red_heels_real.jpg',
        'category': cat_ayakkabi,
        'seller': seller_fashion,
        'variants': [('Kırmızı', '36'), ('Kırmızı', '37'), ('Kırmızı', '38'), ('Kırmızı', '39')]
    },
    {
        'title': 'Lacivert Süet Çift Tokalı Monk Strap Klasik Ayakkabı',
        'desc': 'İtalyan lacivert süet dokulu, çift tokalı lüks tasarım klasik ayakkabı.',
        'price': Decimal('1450.00'),
        'image': 'products/classic_shoes_navy_monk_real.jpg',
        'category': cat_ayakkabi,
        'seller': seller_fashion,
        'variants': [('Lacivert', '42'), ('Lacivert', '43')]
    },
    {
        'title': 'Zarif Bej Taba Deri Klasik Babet Kadın Ayakkabısı',
        'desc': 'Yumuşak taba deri, fiyonk detaylı ve rahat pad tabanlı zamansız babet.',
        'price': Decimal('649.00'),
        'image': 'products/classic_shoes_beige_babet_real.jpg',
        'category': cat_ayakkabi,
        'seller': seller_fashion,
        'variants': [('Bej', '36'), ('Bej', '37'), ('Bej', '38'), ('Bej', '39')]
    },
    {
        'title': 'Beyaz Deri Günlük Unisex Sneaker Spor Ayakkabı',
        'desc': 'Birinci sınıf suni deri, ortopedik yürüyüş tabanlı minimalist beyaz sneaker.',
        'price': Decimal('749.00'),
        'image': 'products/sneakers_white_leather.png',
        'category': cat_ayakkabi,
        'seller': seller_fashion,
        'variants': [('Beyaz', '38'), ('Beyaz', '40'), ('Beyaz', '42'), ('Beyaz', '44')]
    },
    {
        'title': 'Ortopedik Tabanlı Siyah Fileli Spor Ayakkabı',
        'desc': 'Hava alan örgü file kumaş, darbe emici eva tabanlı siyah fitness ayakkabısı.',
        'price': Decimal('689.00'),
        'image': 'products/sneakers_black_mesh.png',
        'category': cat_ayakkabi,
        'seller': seller_fashion,
        'variants': [('Siyah', '40'), ('Siyah', '41'), ('Siyah', '42'), ('Siyah', '43')]
    },

    # --- SAAT & AKSESUAR & ÇANTA ---
    {
        'title': 'Siyah Deri Şal Detaylı Klasik Omuz Çantası',
        'desc': 'İpek şal aksesuar hediyeli, mıknatıs kapaklı siyah deri şık kadın omuz çantası.',
        'price': Decimal('699.00'),
        'image': 'products/bag_shoulder_black_classic_scarf.png',
        'category': cat_aksesuar,
        'seller': seller_fashion,
        'variants': [('Siyah', 'Standart')]
    },
    {
        'title': 'Bej Hakiki Deri İkili Omuz Çanta Seti',
        'desc': 'Büyük omuz çantası ve portföy çanta içeren ikili kaliteli bej deri set.',
        'price': Decimal('849.00'),
        'image': 'products/bag_shoulder_beige_set.png',
        'category': cat_aksesuar,
        'seller': seller_fashion,
        'variants': [('Bej', 'Standart')]
    },
    {
        'title': 'Yarım Ay Model Siyah Şık Kadın Omuz Çantası',
        'desc': 'Trend yarım ay formu, fermuarlı kapamalı kompakt ve zarif siyah çanta.',
        'price': Decimal('549.00'),
        'image': 'products/bag_shoulder_half_moon.png',
        'category': cat_aksesuar,
        'seller': seller_fashion,
        'variants': [('Siyah', 'Standart')]
    },
    {
        'title': 'Ergonomik Laptop & Seyahat Sırt Çantası',
        'desc': '15.6 inç laptop korumalı, USB şarj portlu ve su geçirmez teknolojik sırt çantası.',
        'price': Decimal('799.00'),
        'image': 'products/bag_backpack_tech.png',
        'category': cat_aksesuar,
        'seller': seller_tekno,
        'variants': [('Siyah', 'Standart')]
    },
    {
        'title': 'Polarize Siyah Kemik Çerçeve Güneş Gözlüğü',
        'desc': 'UV400 korumalı polarize siyah camlı, zamansız siyah kemik çerçeve gözlük.',
        'price': Decimal('349.90'),
        'image': 'products/accessory_sunglasses_wayfarer_real.png',
        'category': cat_aksesuar,
        'seller': seller_fashion,
        'variants': [('Siyah', 'Standart')]
    },
    {
        'title': 'Klasik Altın Çerçeveli Damla Havacı Gözlüğü',
        'desc': 'İnce altın kaplama metal çerçeveli, haki camlı efsane aviator havacı gözlüğü.',
        'price': Decimal('429.00'),
        'image': 'products/accessory_sunglasses_aviator_real.png',
        'category': cat_aksesuar,
        'seller': seller_fashion,
        'variants': [('Altın', 'Standart')]
    },
    {
        'title': 'Retro Kahverengi Cat-Eye Kadın Güneş Gözlüğü',
        'desc': 'Kaplumbağa desenli çerçeve, çekik kedi gözü tasarımlı retro kadın gözlüğü.',
        'price': Decimal('299.90'),
        'image': 'products/accessory_sunglasses_cateye_real.png',
        'category': cat_aksesuar,
        'seller': seller_fashion,
        'variants': [('Kahverengi', 'Standart')]
    },
    {
        'title': 'Paslanmaz Çelik Kordon Lüks Erkek Kol Saati',
        'desc': 'Gümüş çelik kordon, lacivert kronometreli kadran ve takvimli erkek saati.',
        'price': Decimal('1299.00'),
        'image': 'products/accessory_watch_silver_steel_real.png',
        'category': cat_aksesuar,
        'seller': seller_fashion,
        'variants': [('Gümüş', 'Standart')]
    },
    {
        'title': 'Hakiki Kahverengi Deri Kordon Klasik Erkek Saat',
        'desc': 'Kahverengi hakiki deri kayış, gümüş kasa ve beyaz minimalist kadranlı erkek saat.',
        'price': Decimal('899.90'),
        'image': 'products/accessory_watch_brown_leather_real.png',
        'category': cat_aksesuar,
        'seller': seller_fashion,
        'variants': [('Kahverengi', 'Standart')]
    },
    {
        'title': 'Rose Gold İnce Hasır Çelik Kadın Kol Saati',
        'desc': 'Pembe altın kaplama zarif çelik kordon, kristal taş detaylı şık kadın saati.',
        'price': Decimal('749.90'),
        'image': 'products/accessory_watch_rose_gold_real.png',
        'category': cat_aksesuar,
        'seller': seller_fashion,
        'variants': [('Rose Gold', 'Standart')]
    },

    # --- TAKILAR ---
    {
        'title': 'Erkek 925 Ayar Gümüş Kaplama Gurmet Zincir Set',
        'desc': 'Zarif gurmet zincir kolye ve uyumlu bileklikten oluşan şık erkek kombin seti.',
        'price': Decimal('499.00'),
        'image': 'products/erkek_gurmet_zincir_kolye_bileklik_set.png',
        'category': cat_taki,
        'seller': seller_fashion,
        'variants': [('Gümüş', 'Standart')]
    },
    {
        'title': 'Oksitli Gümüş İşlemeli Örgü Desen Erkek Bileklik',
        'desc': 'Antik oksit gümüş görünümlü, el işçiliği örgü desenli karizmatik bileklik.',
        'price': Decimal('329.00'),
        'image': 'products/oksitli_gumus_orgu_erkek_bileklik.png',
        'category': cat_taki,
        'seller': seller_fashion,
        'variants': [('Oksit Gümüş', 'Standart')]
    },
    {
        'title': 'Desenli Çelik Baklalı Timsah Logolu Erkek Bileklik',
        'desc': 'Paslanmaz çelik baklalı, timsah logolu dayanıklı erkek bilekliği.',
        'price': Decimal('389.00'),
        'image': 'products/timsah_logolu_celik_baklali_erkek_bileklik.png',
        'category': cat_taki,
        'seller': seller_fashion,
        'variants': [('Çelik', 'Standart')]
    },
    {
        'title': 'Doğal Lav Taşı ve Rose Gold Detaylı Çelik Erkek Bileklik',
        'desc': 'Doğal siyah lav taşı boncuklar ve rose gold çelik aralıklarla tasarlanmış erkek bileklik.',
        'price': Decimal('299.00'),
        'image': 'products/dogal_lav_tasi_rose_gold_celik_bileklik.png',
        'category': cat_taki,
        'seller': seller_fashion,
        'variants': [('Siyah', 'Standart')]
    },
    {
        'title': 'Antik Yunan Motifli Gravürlü Ağır Çelik Erkek Künye Bileklik',
        'desc': 'Geniş künye plakalı, yunan motifi gravür işlemeli ağır çelik erkek bileklik.',
        'price': Decimal('459.00'),
        'image': 'products/yunan_motifli_agir_celik_kunye_bileklik.png',
        'category': cat_taki,
        'seller': seller_fashion,
        'variants': [('Gümüş Çelik', 'Standart')]
    },
    {
        'title': 'Deniz Yıldızı ve İnci Detaylı Plaj Saç Zinciri',
        'desc': 'Yaz ve plaj kombinleri için altın kaplama deniz yıldızı ve doğal inci süslemeli saç zinciri.',
        'price': Decimal('249.00'),
        'image': 'products/user_hair_starfish_chain.png',
        'category': cat_taki,
        'seller': seller_fashion,
        'variants': [('Altın', 'Standart')]
    },
    {
        'title': 'Gelin Kristal Taşlı Yaprak Motifli Lüks Yan Saç Tokası',
        'desc': 'Düğün ve nişan için ışıltılı kristal taşlı yaprak motifli el yapımı yan saç tarağı.',
        'price': Decimal('389.00'),
        'image': 'products/user_hair_silver_leaf_comb.png',
        'category': cat_taki,
        'seller': seller_fashion,
        'variants': [('Gümüş', 'Standart')]
    },
    {
        'title': 'Bohem Kristal Taşlı Alınlık & Saç Zinciri Taç',
        'desc': 'Bohem gelin ve özel gün kombinleri için alına sarkan sallantılı kristal saç tacı.',
        'price': Decimal('429.00'),
        'image': 'products/user_hair_boho_forehead_chain.png',
        'category': cat_taki,
        'seller': seller_fashion,
        'variants': [('Gümüş', 'Standart')]
    },

    # --- ELEKTRONİK & TEKNOLOJİ ---
    {
        'title': 'Ultra HD Pro Aynasız Dijital Fotoğraf Makinesi',
        'desc': '4K Video kaydı, 24MP sensör ve Wi-Fi bağlantılı profesyonel kompakt fotoğraf makinesi.',
        'price': Decimal('14990.00'),
        'image': 'products/camera.jpg',
        'category': cat_elektronik,
        'seller': seller_tekno,
        'variants': [('Siyah', 'Standart')]
    },
    {
        'title': 'Gürültü Engelleyici Kablosuz Kulak Üstü Kulaklık',
        'desc': 'Aktif Gürültü Engelleme (ANC), 40 saat pil ömrü ve yüksek çözünürlüklü ses veren bluetooth kulaklık.',
        'price': Decimal('2499.00'),
        'image': 'products/headphones.jpg',
        'category': cat_elektronik,
        'seller': seller_tekno,
        'variants': [('Siyah', 'Standart'), ('Gümüş', 'Standart')]
    },
    {
        'title': 'Taşınabilir Yüksek Sesli Bluetooth Hoparlör',
        'desc': 'IPX7 Su geçirmezlik, 12 saat kesintisiz müzik ve güçlü bas performanslı taşınabilir hoparlör.',
        'price': Decimal('1299.00'),
        'image': 'products/speaker.jpg',
        'category': cat_elektronik,
        'seller': seller_tekno,
        'variants': [('Siyah', 'Standart')]
    },

    # --- ÇOCUK & BEBEK ---
    {
        'title': 'Organik Çizgili Desenli Mavi Bebek Body Zıbın',
        'desc': '%100 Organik ege pamuğu, anti-alerjik çıtçıtlı şirin mavi bebek body.',
        'price': Decimal('189.00'),
        'image': 'products/baby_clothing_body_blue.png',
        'category': cat_bebek,
        'seller': seller_fashion,
        'variants': [('Mavi', '0-3 Ay'), ('Mavi', '3-6 Ay'), ('Mavi', '6-12 Ay')]
    },
    {
        'title': 'Pamuklu Çıtçıtlı Kısa Kollu Beyaz Bebek Body Zıbın',
        'desc': 'Yumuşak taranmış pamuk, kaşındırmayan etiketli temel beyaz bebek zıbın.',
        'price': Decimal('169.00'),
        'image': 'products/baby_clothing_body_white.png',
        'category': cat_bebek,
        'seller': seller_fashion,
        'variants': [('Beyaz', '0-3 Ay'), ('Beyaz', '3-6 Ay'), ('Beyaz', '6-12 Ay')]
    },
    {
        'title': 'Desenli Şirin Yazlık Pamuklu Bebek Romper Tulum',
        'desc': 'Bebekler için hava alan nefesli pamuklu yazlık desenli kısa tulum.',
        'price': Decimal('249.00'),
        'image': 'products/baby_clothing_romper.png',
        'category': cat_bebek,
        'seller': seller_fashion,
        'variants': [('Desenli', '3-6 Ay'), ('Desenli', '6-12 Ay')]
    },
]

# Insert/Update all items in database
created_count = 0
updated_count = 0

for item in catalog:
    product, created = Product.objects.update_or_create(
        title=item['title'],
        defaults={
            'description': item['desc'],
            'base_price': item['price'],
            'image': item['image'],
            'category': item['category'],
            'seller': item['seller'],
        }
    )
    
    if created:
        created_count += 1
    else:
        updated_count += 1
        
    # Ensure variants
    for color, size in item['variants']:
        existing_variant = ProductVariant.objects.filter(product=product, color=color, size=size).first()
        if not existing_variant:
            sku_code = f"SKU-{product.id}-{uuid.uuid4().hex[:6].upper()}"
            ProductVariant.objects.create(
                product=product,
                color=color,
                size=size,
                price=item['price'],
                stock=25,
                sku=sku_code
            )

print(f"\nSuccessfully organized catalog!")
print(f"Created: {created_count} new products")
print(f"Updated: {updated_count} existing products")
