import os
import sys
import django
import uuid
import random
from decimal import Decimal

sys.path.insert(0, os.path.abspath('.'))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'marketplace_project.settings')
django.setup()

from marketplace.models import Category, Product, ProductVariant, ProductReview, SellerProfile, CustomUser

print("Starting targeted category organization and feature enrichment...")

# Sellers & Users for reviews
seller_tekno = SellerProfile.objects.filter(user__username='tech_seller').first() or SellerProfile.objects.first()
seller_fashion = SellerProfile.objects.filter(user__username='fashion_seller').first() or SellerProfile.objects.first()
customer_users = list(CustomUser.objects.filter(is_staff=False))
if not customer_users:
    customer_users = [CustomUser.objects.first()]

def get_cat(name, parent=None, slug=None):
    if not slug:
        slug = name.lower().replace(' ', '-').replace('&', 've').replace('ç', 'c').replace('ğ', 'g').replace('ı', 'i').replace('ö', 'o').replace('ş', 's').replace('ü', 'u')
    cat, _ = Category.objects.get_or_create(name=name, defaults={'parent': parent, 'slug': slug})
    if parent and cat.parent != parent:
        cat.parent = parent
        cat.save()
    return cat

# Categories to clean & enrich
cat_aksesuar = get_cat('Saat & Aksesuar')
cat_taki = get_cat('Takılar')
cat_elektronik = get_cat('Elektronik & Teknoloji')
cat_bebek = get_cat('Çocuk & Bebek')

# Categories to KEEP INTACT (Giyim, Ayakkabı, Kozmetik)
protected_cats = list(Category.objects.filter(name__in=['Giyim & Moda', 'Ayakkabı', 'Kozmetik & Kişisel Bakım', 'Kozmetik & Makyaj'])) + list(Category.objects.filter(parent__name__in=['Giyim & Moda', 'Ayakkabı', 'Kozmetik & Kişisel Bakım', 'Kozmetik & Makyaj']))
protected_cat_ids = set(c.id for c in protected_cats)

# Clean up old dummy products in target categories ONLY
target_cats = [cat_aksesuar, cat_taki, cat_elektronik, cat_bebek] + list(Category.objects.filter(parent__in=[cat_aksesuar, cat_taki, cat_elektronik, cat_bebek]))
target_cats = [c for c in target_cats if c.id not in protected_cat_ids]

dummy_products = Product.objects.filter(category__in=target_cats)
for p in dummy_products:
    ProductVariant.objects.filter(product=p).delete()
    ProductReview.objects.filter(product=p).delete()
    p.delete()

print(f"Cleaned up {dummy_products.count()} old products in non-protected target categories.")

# Target Categories Real Items
target_catalog = [
    # --- SAAT & AKSESUAR ---
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
        'title': 'Hakiki Deri Çok Bölmeli Erkek Cüzdanı',
        'desc': 'RFID korumalı, hakiki taba derisinden imal edilmiş çok gözlü erkek cüzdanı.',
        'price': Decimal('389.00'),
        'image': 'products/accessory_wallet_leather.png',
        'category': cat_aksesuar,
        'seller': seller_fashion,
        'variants': [('Taba', 'Standart'), ('Siyah', 'Standart')]
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
    {
        'title': 'Dokunmatik Ekran Siyah Akıllı Spor Saat',
        'desc': 'AMOLED renkli ekran, nabız takibi ve su geçirmez siyah silikon kordonlu akıllı saat.',
        'price': Decimal('1099.00'),
        'image': 'products/accessory_watch_smartwatch_real.png',
        'category': cat_aksesuar,
        'seller': seller_tekno,
        'variants': [('Siyah', 'Standart')]
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
    {
        'title': 'Altın Yaprak ve İnci Motifli Yan Saç Tarağı & Tokası',
        'desc': 'Zarif altın kaplama dallar ve inci süslemeli şık saç tarağı.',
        'price': Decimal('349.00'),
        'image': 'products/user_hair_gold_leaf_branch.png',
        'category': cat_taki,
        'seller': seller_fashion,
        'variants': [('Altın', 'Standart')]
    },
    {
        'title': 'İncili ve Kristal Taşlı Lüks Gelin Tacı',
        'desc': 'Gelinlik kombinleri için pırlanta ışıltılı kristal ve inci taç.',
        'price': Decimal('589.00'),
        'image': 'products/hair_accessory_pearl_comb_real.jpg',
        'category': cat_taki,
        'seller': seller_fashion,
        'variants': [('Gümüş Kristal', 'Standart')]
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
    {
        'title': 'Ergonomik Kablosuz Lazer Oyuncu Mouse',
        'desc': '16000 DPI Optik sensör, RGB aydınlatma ve 6 programlanabilir tuşlu profesyonel mouse.',
        'price': Decimal('599.00'),
        'image': 'products/mouse.jpg',
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
    {
        'title': 'Yumuşak Dokulu Beli Lastikli Bebek Eşofman Altı',
        'desc': 'Bebeğinizin hareket özgürlüğünü kısıtlamayan esnek beli lastikli pamuklu eşofman altı.',
        'price': Decimal('199.00'),
        'image': 'products/baby_clothing_pants.png',
        'category': cat_bebek,
        'seller': seller_fashion,
        'variants': [('Gri', '3-6 Ay'), ('Gri', '6-12 Ay')]
    },
    {
        'title': 'Atopik Ciltler İçin Doğal Bebek Nemlendirici Bakım Kremi',
        'desc': 'Parabensiz, organik papatya özlü hassas bebek cildini yatıştıran nemlendirici krem.',
        'price': Decimal('289.00'),
        'image': 'products/baby_moisturizer_cream.png',
        'category': cat_bebek,
        'seller': seller_fashion,
        'variants': [('200ml', 'Standart')]
    },
    {
        'title': 'Bebekler İçin Hijyenik İzotonik Serum Fizyolojik Ampul (20li)',
        'desc': 'Bebek burun ve göz temizliği için steril 20 adet izotonik deniz suyu ampulü.',
        'price': Decimal('149.00'),
        'image': 'products/baby_saline_ampoules.png',
        'category': cat_bebek,
        'seller': seller_fashion,
        'variants': [('20li Ampul', 'Standart')]
    },
]

# Insert target catalog items
created_count = 0
for item in target_catalog:
    product = Product.objects.create(
        title=item['title'],
        description=item['desc'],
        base_price=item['price'],
        image=item['image'],
        category=item['category'],
        seller=item['seller']
    )
    created_count += 1
    for color, size in item['variants']:
        sku_code = f"SKU-TAR-{product.id}-{uuid.uuid4().hex[:5].upper()}"
        ProductVariant.objects.create(
            product=product,
            color=color,
            size=size,
            price=item['price'],
            stock=30,
            sku=sku_code
        )

print(f"Successfully populated target categories with {created_count} real unique products!")

# --- FEATURE ENRICHMENT ACROSS ALL PRODUCTS IN DATABASE ---
print("\nEnriching features (Reviews, Ratings, Dominant Colors, Variants) across ALL products...")

sample_comments = [
    "Ürün harika, kumaş kalitesi ve dokusu mükemmel! Tam beden alabilirsiniz.",
    "Paketleme çok özenliydi, kargo ertesi gün ulaştı. Satıcıya teşekkürler.",
    "Beklediğimden de kaliteli ve canlı fotoğraftakiyle birebir aynı geldi.",
    "Fiyatına göre performansı süper, kesinlikle tavsiye ederim.",
    "Birebir orijinal ve çok şık, çevremdeki herkes nereden aldığımı sordu!"
]

all_products = Product.objects.all()
enriched_count = 0

for p in all_products:
    # 1. Ensure rating & review count
    if p.review_count == 0 or p.average_rating == Decimal('0.00'):
        p.average_rating = Decimal(str(round(random.uniform(4.3, 5.0), 2)))
        p.review_count = random.randint(8, 35)
        p.save()
        
        # Add 2 sample reviews
        for i in range(2):
            user = random.choice(customer_users)
            ProductReview.objects.get_or_create(
                product=p,
                user=user,
                defaults={
                    'rating': random.randint(4, 5),
                    'comment': random.choice(sample_comments),
                    'is_approved': True,
                    'helpful_count': random.randint(3, 12)
                }
            )
            
    # 2. Ensure dominant color & palette
    if not p.dominant_color:
        colors = ['#1A1A1A', '#F5F5F5', '#2B4C7E', '#D4AF37', '#8B0000', '#2E8B57']
        p.dominant_color = random.choice(colors)
        p.color_palette = [p.dominant_color, '#FFFFFF', '#CCCCCC']
        p.save()
        
    # 3. Ensure variants
    if not p.variants.exists():
        sku_code = f"SKU-GEN-{p.id}-{uuid.uuid4().hex[:5].upper()}"
        ProductVariant.objects.create(
            product=p,
            color='Standart',
            size='Standart',
            price=p.base_price,
            stock=25,
            sku=sku_code
        )
        
    enriched_count += 1

print(f"Successfully enriched features for {enriched_count} products across the entire database!")
