import os
import sys
import django

sys.path.insert(0, os.path.abspath('.'))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'marketplace_project.settings')
django.setup()

from marketplace.models import Product, ProductVariant, Category, SellerProfile

seller = SellerProfile.objects.first()

cat_giyim, _ = Category.objects.get_or_create(name='Giyim & Moda')
cat_aksesuar, _ = Category.objects.get_or_create(name='Saat & Aksesuar')
cat_ayakkabi, _ = Category.objects.get_or_create(name='Ayakkabı')
cat_elektronik, _ = Category.objects.get_or_create(name='Elektronik & Teknoloji')
cat_kozmetik, _ = Category.objects.get_or_create(name='Kozmetik & Kişisel Bakım')
cat_cocuk, _ = Category.objects.get_or_create(name='Çocuk & Bebek')

# 100% Unique product mapping library
unique_catalog = [
    # SAAT & AKSESUAR
    {
        'title': 'Lüks Lazer Kesim Altın Kasa Kol Saati',
        'desc': 'Çizilmez safir kristal camlı, altın kaplama çelik kasalı ve otomatik mekanizmalı lüks erkek kol saati.',
        'price': 1850.00,
        'img': 'products/accessory_watch_gold.png',
        'cat': cat_aksesuar,
        'colors': ['Altın', 'Altın-Siyah']
    },
    {
        'title': 'Hakiki Kahverengi Deri Kordonlu Klasik Saat',
        'desc': 'İtalyan deri kordonlu, paslanmaz kronometre kadranlı ve 50m su geçirmez klasik erkek saati.',
        'price': 1450.00,
        'img': 'products/accessory_watch_leather.png',
        'cat': cat_aksesuar,
        'colors': ['Kahverengi', 'Taba']
    },
    {
        'title': 'Çelik Kordonlu Spor Otomatik Erkek Saati',
        'desc': 'Mat gri çelik kordonlu, takvim göstergeli ve gece parlayan fosforlu kadranlı spor saat.',
        'price': 1650.00,
        'img': 'products/accessory_watch_steel.png',
        'cat': cat_aksesuar,
        'colors': ['Gümüş Gri', 'Siyah']
    },
    {
        'title': 'Klasik Aviator Polarize Güneş Gözlüğü',
        'desc': 'UV400 korumalı polarize camlı, altın kaplama ince metal çerçeveli zamansız aviator tasarım.',
        'price': 720.00,
        'img': 'products/accessory_sunglasses_aviator.png',
        'cat': cat_aksesuar,
        'colors': ['Altın-Siyah', 'Gümüş-Mavi']
    },
    {
        'title': 'Hakiki Deri Çok Bölmeli Erkek Cüzdanı',
        'desc': 'RFID kart korumalı, hakiki dana derisinden üretilmiş çok gözlü şık erkek cüzdanı.',
        'price': 480.00,
        'img': 'products/accessory_wallet_leather.png',
        'cat': cat_aksesuar,
        'colors': ['Siyah', 'Kahverengi', 'Taba']
    },
    {
        'title': 'Dikiş Detaylı Hakiki Deri Erkek Kemeri',
        'desc': '%100 hakiki deriden üretilmiş, paslanmaz çelik tokalı ve kot/kumaş pantolonla uyumlu deri kemer.',
        'price': 390.00,
        'img': 'products/accessory_belt_leather.png',
        'cat': cat_aksesuar,
        'colors': ['Siyah', 'Taba']
    },
    {
        'title': 'Bordo Süet Detaylı Tasarım Omuz Çantası',
        'desc': 'Ayarlanabilir zincir askılı, bordo süet dokulu ve altın kilit aksesuarlı şık kadın omuz çantası.',
        'price': 1350.00,
        'img': 'products/bag_shoulder_maroon.png',
        'cat': cat_aksesuar,
        'colors': ['Bordo', 'Siyah']
    },
    {
        'title': 'Taba Deri Büyük Boy Seyahat & El Çantası',
        'desc': 'Geniş iç hacimli, çok bölmeli ve su geçirmez astarlı birinci sınıf taba deri el çantası.',
        'price': 1580.00,
        'img': 'products/bag_shoulder_leather.png',
        'cat': cat_aksesuar,
        'colors': ['Taba', 'Kahverengi']
    },
    {
        'title': 'Teknolojik Sırt Çantası (Laptop Bölmeli)',
        'desc': 'USB şarj portlu, su geçirmez kumaştan üretilmiş 15.6 inç laptop korumalı ergonomik sırt çantası.',
        'price': 890.00,
        'img': 'products/bag_backpack_tech.png',
        'cat': cat_aksesuar,
        'colors': ['Siyah', 'Koyu Gri']
    },

    # GİYİM & MODA
    {
        'title': 'Zümrüt Yeşili Saten Gece Elbisesi',
        'desc': 'Özel davetler için tasarlanmış, yırtmaçlı ve sırt dekolteli dökümlü zümrüt yeşili saten abiye elbise.',
        'price': 2100.00,
        'img': 'products/dress_emerald_satin.png',
        'cat': cat_giyim,
        'colors': ['Zümrüt Yeşili', 'Siyah']
    },
    {
        'title': 'Kırmızı Çiçek Desenli Şifon Yazlık Elbise',
        'desc': 'Nefes alan ince şifon kumaştan üretilmiş, belden bağlamalı ve uçuş uçuş kırmızı çiçekli elbise.',
        'price': 1250.00,
        'img': 'products/dress_red_floral.png',
        'cat': cat_giyim,
        'colors': ['Kırmızı Desenli', 'Mavi Desenli']
    },
    {
        'title': 'Siyah Kadife Askılı Mini Abiye Elbise',
        'desc': 'Esnek ithal kadife kumaş, derin yırtmaçlı ve şık göğüs dekolteli siyah mini gece elbisesi.',
        'price': 1680.00,
        'img': 'products/dress_black_velvet.png',
        'cat': cat_giyim,
        'colors': ['Siyah', 'Koyu Kırmızı']
    },
    {
        'title': 'Klasik Bej Kruvaze Trençkot',
        'desc': 'Su ve rüzgar geçirmez pamuklu gabardin kumaş, kemerli ve krpü detaylı zamansız bej trençkot.',
        'price': 2450.00,
        'img': 'products/trench_classic_beige.png',
        'cat': cat_giyim,
        'colors': ['Bej', 'Taba', 'Siyah']
    },
    {
        'title': 'Siyah Kuştüyü Dolgulu Kapüşonlu Şişme Mont',
        'desc': 'Soğuk kış günleri için ultra sıcak tutan, rüzgara dayanıklı ve su itici siyah şişme kışlık mont.',
        'price': 2950.00,
        'img': 'products/coat_black_puffer.png',
        'cat': cat_giyim,
        'colors': ['Siyah', 'Mat Gri']
    },
    {
        'title': 'İtalyan Stil Kahverengi Aviator Kürklü Kaban',
        'desc': 'İçi yumuşacık peluş kürk kaplı, hakiki deri biye detaylı premium kahverengi süet kaban.',
        'price': 3850.00,
        'img': 'products/coat_aviator_brown.png',
        'cat': cat_giyim,
        'colors': ['Kahverengi', 'Koyu Taba']
    },
    {
        'title': 'Lacivert Çizgili Klasik İpek Karışımlı Gömlek',
        'desc': '%100 pamuk iplikten dokunmuş, kol düğmesi uyumlu ve slim fit kesim çizgili erkek gömlek.',
        'price': 890.00,
        'img': 'products/shirt_striped_white_real.png',
        'cat': cat_giyim,
        'colors': ['Lacivert Çizgili', 'Mavi Çizgili']
    },
    {
        'title': 'Siyah İtalyan Kesim Kumaş Pantolon',
        'desc': 'Dökümlü kaliteli kumaş, ütü tutan pili detaylı ve modern düz kesim siyah erkek/kadın kumaş pantolon.',
        'price': 950.00,
        'img': 'products/pants_black_tailored_v1.png',
        'cat': cat_giyim,
        'colors': ['Siyah', 'Koyu Gri']
    },
    {
        'title': 'Açık Mavi Mom Fit Yüksek Bel Kot Pantolon',
        'desc': '%100 pamuklu kaliteli kot kumaş, yüksek bel ve rahat oturan mom fit kesim mavi jean.',
        'price': 780.00,
        'img': 'products/jean_mom_fit_light.png',
        'cat': cat_giyim,
        'colors': ['Açık Mavi', 'Koyu Mavi']
    },
    {
        'title': 'Leopar Desenli Yırtmaçlı Saten Etek',
        'desc': 'Beli lastikli esnek kumaş, yan yırtmaçlı ve şık leopar desenli midi boy saten etek.',
        'price': 650.00,
        'img': 'products/skirt_leopard.png',
        'cat': cat_giyim,
        'colors': ['Leopar Desen', 'Siyah']
    },

    # KOZMETİK & KİŞİSEL BAKIM
    {
        'title': 'Niş Odunsu & Amber Esanslı Özel Parfüm (100ml)',
        'desc': 'Fransız esanslarıyla harmanlanmış, amber, vanilya ve sandal ağacı notalı 48 saat kalıcı lüks parfüm.',
        'price': 1850.00,
        'img': 'products/perfume.png',
        'cat': cat_kozmetik,
        'colors': ['100 ml']
    },
    {
        'title': 'Mat Kırmızı Kalıcı Likit Ruj (Red Velvet)',
        'desc': 'Dudakları kurutmayan vitamin E destekli, 16 saat kalıcı mat kırmızı likit ruj.',
        'price': 340.00,
        'img': 'products/lipstick.png',
        'cat': cat_kozmetik,
        'colors': ['Kırmızı Velvet', 'Bordo']
    },
    {
        'title': '12 Renkli Doğal İşıltılı Göz Farı Paleti',
        'desc': 'Yüksek pigmentli mat ve ışıltılı toprak tonlarından oluşan tozutmaz 12 renkli profesyonel far paleti.',
        'price': 490.00,
        'img': 'products/eyeshadow.png',
        'cat': cat_kozmetik,
        'colors': ['Nude Palet', 'Warm Bronze']
    },
    {
        'title': 'Hyalüronik Asit & C Vitamini Cilt Yenileyici Serum',
        'desc': 'Cilde anında ışıltı veren, gözenek sıkılaştırıcı ve kırışıklık karşıtı yoğun konsantre C vitamini serumu.',
        'price': 520.00,
        'img': 'products/skincare.png',
        'cat': cat_kozmetik,
        'colors': ['30 ml']
    },
    {
        'title': 'Organik Argan Yağlı Besleyici Saç Şampuanı (500ml)',
        'desc': 'Sülfatsız ve tuzsuz formülüyle yıpranmış saçları onaran, parlaklık kazandıran organik şampuan.',
        'price': 220.00,
        'img': 'products/shampoo.png',
        'cat': cat_kozmetik,
        'colors': ['500 ml']
    },

    # TAKI & MÜCEVHER
    {
        'title': '925 Ayar Gümüş İnce Taşlı Kadın Kolye',
        'desc': 'Zirkon taş detaylı, kararmayan 925 ayar gerçek gümüş zarafet kolesi.',
        'price': 580.00,
        'img': 'products/necklace.png',
        'cat': cat_aksesuar,
        'colors': ['Gümüş', 'Gold Kaplama']
    },
    {
        'title': 'Zirkon Taşlı Ayarlanabilir Gümüş Yüzük',
        'desc': 'Pırlanta montürlü, ışığı mükemmel yansıtan berrak zirkon taşlı kadın yüzük.',
        'price': 420.00,
        'img': 'products/ring.png',
        'cat': cat_aksesuar,
        'colors': ['Gümüş', 'Rose Gold']
    },
    {
        'title': 'Şık Halka İncili Gümüş Küpe',
        'desc': 'Gerçek tatlı su incisi detaylı, antialerjik gümüş sallantılı halka küpe.',
        'price': 360.00,
        'img': 'products/earrings.png',
        'cat': cat_aksesuar,
        'colors': ['Gümüş-İnci']
    }
]

print(f"Applying {len(unique_catalog)} unique products to database...")

prods = list(Product.objects.all())

for i, item in enumerate(unique_catalog):
    if i < len(prods):
        p = prods[i]
        p.title = item['title']
        p.description = item['desc']
        p.base_price = item['price']
        p.image = item['img']
        p.category = item['cat']
        if seller:
            p.seller = seller
        p.save()

        # Update variants nicely
        existing_variants = list(p.variants.all())
        for idx, color in enumerate(item['colors']):
            if idx < len(existing_variants):
                v = existing_variants[idx]
                v.color = color
                v.stock = 35
                v.save()
            else:
                ProductVariant.objects.create(
                    product=p,
                    color=color,
                    size='',
                    stock=35,
                    sku=f"UNIQUE-{p.id}-{color}"
                )

print("ALL PRODUCTS UPDATED WITH 100% UNIQUE IMAGES AND DETAILS PERFECTLY!")
