import os
import sys
import django
import uuid
from decimal import Decimal

sys.path.insert(0, os.path.abspath('.'))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'marketplace_project.settings')
django.setup()

from marketplace.models import Category, Product, ProductVariant, SellerProfile, ProductReview

print("Fixing Giyim & Moda category with exact real product photos...")

# 1. Fetch main Giyim & Moda category and subcategories
cat_giyim_main, _ = Category.objects.get_or_create(name='Giyim & Moda', defaults={'slug': 'giyim-ve-moda'})

def get_subcat(name, slug=None):
    if not slug:
        slug = name.lower().replace(' ', '-').replace('&', 've').replace('ç', 'c').replace('ğ', 'g').replace('ı', 'i').replace('ö', 'o').replace('ş', 's').replace('ü', 'u')
    cat, _ = Category.objects.get_or_create(name=name, defaults={'parent': cat_giyim_main, 'slug': slug})
    if cat.parent != cat_giyim_main:
        cat.parent = cat_giyim_main
        cat.save()
    return cat

sub_gomlek = get_subcat('Gömlek & Tişört')
sub_bluz = get_subcat('Bluz')
sub_elbise = get_subcat('Elbise & Tulum')
sub_etek = get_subcat('Etek')
sub_mont = get_subcat('Mont & Ceket')
sub_hirka = get_subcat('Hırka & Yelek')
sub_pantolon = get_subcat('Pantolon & Jean')
sub_pijama = get_subcat('Pijama & Kombin Setleri')

# All category nodes to clean up dummy items
all_giyim_cats = [cat_giyim_main, sub_gomlek, sub_bluz, sub_elbise, sub_etek, sub_mont, sub_hirka, sub_pantolon, sub_pijama] + list(Category.objects.filter(parent=cat_giyim_main))

# Clean up existing products in all giyim categories to build clean catalog
old_products = Product.objects.filter(category__in=all_giyim_cats)
for p in old_products:
    ProductVariant.objects.filter(product=p).delete()
    ProductReview.objects.filter(product=p).delete()
    p.delete()

print(f"Cleaned up {old_products.count()} old products in Giyim & Moda categories.")

seller_fashion = SellerProfile.objects.filter(user__username='fashion_seller').first() or SellerProfile.objects.first()

# 45+ Real Clothing Items
giyim_items = [
    # GÖMLEK & TİŞÖRT
    {
        'title': 'Mavi İtalyan Slim Fit Takım Elbise Gömleği',
        'desc': '%100 Pamuklu nefes alan kumaş, leke tutmaz yaka ve slim fit İtalyan kesim şık erkek gömlek.',
        'price': Decimal('549.90'),
        'image': 'products/shirt_blue_suit_real.png',
        'category': sub_gomlek,
        'variants': [('Mavi', 'S'), ('Mavi', 'M'), ('Mavi', 'L'), ('Mavi', 'XL')]
    },
    {
        'title': 'Çizgili Klasik Pamuklu Erkek Gömlek',
        'desc': 'Mavi-beyaz ince çizgili, kol manşet detaylı klasik stil günlük erkek gömlek.',
        'price': Decimal('499.00'),
        'image': 'products/shirt_striped_white_real.png',
        'category': sub_gomlek,
        'variants': [('Çizgili Mavi', 'M'), ('Çizgili Mavi', 'L'), ('Çizgili Mavi', 'XL')]
    },
    {
        'title': 'Oxford Beyaz Slim Fit Pamuk Erkek Gömlek',
        'desc': 'Zarif Oxford dokuma pamuk kumaş, düğmeli yaka ve şık slim fit beyaz gömlek.',
        'price': Decimal('529.00'),
        'image': 'products/shirt_white_close_real.png',
        'category': sub_gomlek,
        'variants': [('Beyaz', 'S'), ('Beyaz', 'M'), ('Beyaz', 'L'), ('Beyaz', 'XL')]
    },
    {
        'title': 'Sarı Desenli Casual Yazlık Erkek Gömlek',
        'desc': 'Canlı sarı renkli, rahat kesim yıkanmış pamuklu casual gömlek.',
        'price': Decimal('429.50'),
        'image': 'products/shirt_yellow_jeans_real.png',
        'category': sub_gomlek,
        'variants': [('Sarı', 'M'), ('Sarı', 'L')]
    },
    {
        'title': 'Bej Keten Slim Fit Erkek Gömlek',
        'desc': 'Yaz ayları için ferah doğal keten kumaş, bej slim fit erkek gömlek.',
        'price': Decimal('579.00'),
        'image': 'products/shirt_white_beige_real.png',
        'category': sub_gomlek,
        'variants': [('Bej', 'M'), ('Bej', 'L'), ('Bej', 'XL')]
    },
    {
        'title': 'Siyah Destekar Pamuklu Unisex Tişört',
        'desc': '%100 Pamuk birinci sınıf kumaş, önü grafik baskılı şık siyah tişört.',
        'price': Decimal('299.00'),
        'image': 'products/tshirt_destekar_black.png',
        'category': sub_gomlek,
        'variants': [('Siyah', 'S'), ('Siyah', 'M'), ('Siyah', 'L')]
    },
    {
        'title': 'Turuncu Sunset Grafik Baskılı Tişört',
        'desc': 'Gün batımı manzaralı turuncu grafik baskılı salaş kesim t-shirt.',
        'price': Decimal('329.00'),
        'image': 'products/tshirt_orange_sunset.png',
        'category': sub_gomlek,
        'variants': [('Turuncu', 'M'), ('Turuncu', 'L'), ('Turuncu', 'XL')]
    },
    {
        'title': 'Beyaz Grafik Baskılı Oversize Tişört',
        'desc': 'Oversize kesim, yüksek kalite pamuklu beyaz unisex sokak stili tişört.',
        'price': Decimal('349.00'),
        'image': 'products/tshirt_pubg_white.png',
        'category': sub_gomlek,
        'variants': [('Beyaz', 'S'), ('Beyaz', 'M'), ('Beyaz', 'L')]
    },
    {
        'title': 'Siyah Slim Fit Basic Pamuk Tişört',
        'desc': 'Vücudu saran esnek likralı pamuk kumaş temel siyah erkek tişört.',
        'price': Decimal('249.00'),
        'image': 'products/tshirt_suit_black.png',
        'category': sub_gomlek,
        'variants': [('Siyah', 'S'), ('Siyah', 'M'), ('Siyah', 'L'), ('Siyah', 'XL')]
    },

    # BLUZ
    {
        'title': 'Turkuaz Dökümlü Saten Kadın Bluz',
        'desc': 'Şık turkuaz rengi saten dokulu, V yaka dökümlü zarif kadın bluz.',
        'price': Decimal('479.90'),
        'image': 'products/blouse_turquoise.png',
        'category': sub_bluz,
        'variants': [('Turkuaz', 'S'), ('Turkuaz', 'M'), ('Turkuaz', 'L')]
    },
    {
        'title': 'Puantiyeli Viskon Şık Kadın Bluz',
        'desc': 'Siyah üzeri beyaz puantiye desenli, karpuz kol şık günlük ve ofis bluzu.',
        'price': Decimal('399.00'),
        'image': 'products/blouse_polka_dot.png',
        'category': sub_bluz,
        'variants': [('Puantiyeli Siyah', 'S'), ('Puantiyeli Siyah', 'M')]
    },
    {
        'title': 'Kahverengi Degaje Yaka Saten Kadın Bluz',
        'desc': 'Dökümlü degaje yaka, kahverengi parlak saten kumaştan özel davet bluzu.',
        'price': Decimal('459.00'),
        'image': 'products/blouse_brown_cowl.png',
        'category': sub_bluz,
        'variants': [('Kahverengi', 'S'), ('Kahverengi', 'M')]
    },
    {
        'title': 'Deniz Yıldızı Desenli Beyaz Şifon Bluz',
        'desc': 'Nefes alan hafif şifon kumaş, deniz yıldızı motifli beyaz şık bluz.',
        'price': Decimal('419.00'),
        'image': 'products/blouse_white_starfish.png',
        'category': sub_bluz,
        'variants': [('Beyaz', 'S'), ('Beyaz', 'M')]
    },
    {
        'title': 'Beyaz Dik Yaka Zarif Kadın Bluz',
        'desc': 'Yarım dik yaka kesim, kolsuz dökümlü beyaz krepsaten kadın bluz.',
        'price': Decimal('389.00'),
        'image': 'products/blouse_white_mock_neck.png',
        'category': sub_bluz,
        'variants': [('Beyaz', 'S'), ('Beyaz', 'M'), ('Beyaz', 'L')]
    },

    # ELBİSE & TULUM
    {
        'title': 'Zümrüt Yeşili Saten Gece Elbisesi',
        'desc': 'Özel davet ve abiyeler için yırtmaçlı, sırt dekolteli zümrüt yeşili dökümlü saten elbise.',
        'price': Decimal('1290.00'),
        'image': 'products/dress_emerald_satin.png',
        'category': sub_elbise,
        'variants': [('Zümrüt Yeşili', '36'), ('Zümrüt Yeşili', '38'), ('Zümrüt Yeşili', '40')]
    },
    {
        'title': 'Siyah Kadife Lüks Gece Elbisesi',
        'desc': 'Yoğun siyah kadife dokulu, vücudu saran şık gece ve parti elbisesi.',
        'price': Decimal('1150.00'),
        'image': 'products/dress_black_velvet.png',
        'category': sub_elbise,
        'variants': [('Siyah', '36'), ('Siyah', '38')]
    },
    {
        'title': 'Kırmızı Çiçek Desenli Şifon Yazlık Elbise',
        'desc': 'Canlı kırmızı zemin üzerine zarif çiçek baskılı dökümlü şifon elbise.',
        'price': Decimal('689.00'),
        'image': 'products/dress_red_floral.png',
        'category': sub_elbise,
        'variants': [('Kırmızı', 'S'), ('Kırmızı', 'M'), ('Kırmızı', 'L')]
    },
    {
        'title': 'Beyaz Keten Bohemian Dökümlü Elbise',
        'desc': '%100 Keten kumaştan rahat kesim, dantel detaylı bohem beyaz elbise.',
        'price': Decimal('789.00'),
        'image': 'products/dress_white_linen.png',
        'category': sub_elbise,
        'variants': [('Beyaz', 'S'), ('Beyaz', 'M')]
    },
    {
        'title': 'Sarı Fırfırlı Şık Yaz Elbisesi',
        'desc': 'Güneş sarısı renginde, etek ucu fırfırlı neşeli yazlık elbise.',
        'price': Decimal('599.00'),
        'image': 'products/dress_yellow_ruffle.png',
        'category': sub_elbise,
        'variants': [('Sarı', 'S'), ('Sarı', 'M'), ('Sarı', 'L')]
    },
    {
        'title': 'Kırmızı Klasik Kesim Günlük Elbise',
        'desc': 'V yaka şık drapeli, gün boyu konfor sağlayan pamuklu kırmızı elbise.',
        'price': Decimal('549.00'),
        'image': 'products/casual_red_dress.png',
        'category': sub_elbise,
        'variants': [('Kırmızı', '36'), ('Kırmızı', '38'), ('Kırmızı', '40')]
    },
    {
        'title': 'Kemerli Siyah Denim Kadın Tulumu',
        'desc': 'Siyah denim kumaş, belden kemerli ve cepli modern şık tulum.',
        'price': Decimal('799.00'),
        'image': 'products/jumpsuit_black_denim.png',
        'category': sub_elbise,
        'variants': [('Siyah', 'S'), ('Siyah', 'M')]
    },
    {
        'title': 'Keten Dokulu Bej Dökümlü Kadın Tulumu',
        'desc': 'Nefes alan bej keten kumaş, geniş paça dökümlü günlük ve tatil tulumu.',
        'price': Decimal('749.00'),
        'image': 'products/jumpsuit_linen_beige.png',
        'category': sub_elbise,
        'variants': [('Bej', 'S'), ('Bej', 'M'), ('Bej', 'L')]
    },

    # ETEK
    {
        'title': 'Leopar Desenli Saten Midi Etek',
        'desc': 'Yüksek bel, leopar desenli dökümlü saten midi kadın etek.',
        'price': Decimal('489.00'),
        'image': 'products/skirt_leopard.png',
        'category': sub_etek,
        'variants': [('Leopar', 'S'), ('Leopar', 'M'), ('Leopar', 'L')]
    },
    {
        'title': 'Siyah Kruvaze Kesim Şık Etek',
        'desc': 'Önden yırtmaçlı kruvaze bağlamalı siyah kumaş şık etek.',
        'price': Decimal('429.00'),
        'image': 'products/skirt_black_wrap.png',
        'category': sub_etek,
        'variants': [('Siyah', 'S'), ('Siyah', 'M')]
    },
    {
        'title': 'Açık Mavi Kot Mini Etek',
        'desc': 'Açık mavi yıkanmış kot kumaş, cepli klasik denim mini etek.',
        'price': Decimal('379.00'),
        'image': 'products/skirt_denim_mini.png',
        'category': sub_etek,
        'variants': [('Açık Mavi', '34'), ('Açık Mavi', '36'), ('Açık Mavi', '38')]
    },
    {
        'title': 'Puantiyeli Viskon Flared Etek',
        'desc': 'A-kesim dökümlü puantiyeli viskon günlük etek.',
        'price': Decimal('399.00'),
        'image': 'products/skirt_polka_dot.png',
        'category': sub_etek,
        'variants': [('Puantiyeli Siyah', 'S'), ('Puantiyeli Siyah', 'M')]
    },

    # MONT & CEKET & TRENÇKOT
    {
        'title': 'Siyah Kapüşonlu Şişme Kadın/Erkek Mont',
        'desc': 'Rüzgar ve su geçirmez dokulu, elyaf dolgulu sıcak tutan mat siyah şişme mont.',
        'price': Decimal('1499.00'),
        'image': 'products/coat_black_puffer.png',
        'category': sub_mont,
        'variants': [('Siyah', 'M'), ('Siyah', 'L'), ('Siyah', 'XL')]
    },
    {
        'title': 'Kahverengi Süet Kürk Yaka Aviator Ceket',
        'desc': 'İç kısmı yumuşak kürklü, hakiki görünümlü kahverengi aviator tarz ceket.',
        'price': Decimal('1690.00'),
        'image': 'products/coat_aviator_brown.png',
        'category': sub_mont,
        'variants': [('Kahverengi', 'M'), ('Kahverengi', 'L')]
    },
    {
        'title': 'Siyah Deri Görünümlü Şişme Ceket',
        'desc': 'Parlak suni deri kaplama, kalın dolgulu stil sahibi siyah şişme mont.',
        'price': Decimal('1390.00'),
        'image': 'products/coat_leather_puffer.png',
        'category': sub_mont,
        'variants': [('Siyah', 'S'), ('Siyah', 'M'), ('Siyah', 'L')]
    },
    {
        'title': 'Siyah Kapitone Klasik Erkek Mont',
        'desc': 'Baklava kapitone dikişli, hafif ve sıcak tutan klasik siyah erkek mont.',
        'price': Decimal('1290.00'),
        'image': 'products/coat_black_quilted.png',
        'category': sub_mont,
        'variants': [('Siyah', 'M'), ('Siyah', 'L'), ('Siyah', 'XL')]
    },
    {
        'title': 'Gri Bomber Spor Kolej Ceket',
        'desc': 'Gri melanj kumaş, ribana yaka ve manşetli spor bomber ceket.',
        'price': Decimal('989.00'),
        'image': 'products/coat_bomber_gray.png',
        'category': sub_mont,
        'variants': [('Gri', 'M'), ('Gri', 'L')]
    },
    {
        'title': 'Klasik Bej Kruvaze Trençkot',
        'desc': 'Kemerli, kruvaze kapama waterproof bej klasik stil kadın trençkot.',
        'price': Decimal('1490.00'),
        'image': 'products/trench_classic_beige.png',
        'category': sub_mont,
        'variants': [('Bej', '36'), ('Bej', '38'), ('Bej', '40')]
    },
    {
        'title': 'Koyu Kahverengi Kemerli Trençkot',
        'desc': 'Şık koyu kahve tonunda, astarlı ve su tutmaz dökümlü trençkot.',
        'price': Decimal('1390.00'),
        'image': 'products/trench_dark_brown.png',
        'category': sub_mont,
        'variants': [('Koyu Kahve', '36'), ('Koyu Kahve', '38')]
    },
    {
        'title': 'Pudra Bej Dökümlü Trençkot',
        'desc': 'Soft pudra bej tonu, süet dokulu dökümlü baharlık trençkot.',
        'price': Decimal('1290.00'),
        'image': 'products/trench_pink_beige.png',
        'category': sub_mont,
        'variants': [('Pudra Bej', '36'), ('Pudra Bej', '38')]
    },
    {
        'title': 'Adaçayı Yeşili Şık Trençkot',
        'desc': 'Modern adaçayı yeşili renkli, omuz apoletli kruvaze trençkot.',
        'price': Decimal('1350.00'),
        'image': 'products/trench_sage_green.png',
        'category': sub_mont,
        'variants': [('Adaçayı Yeşili', '38'), ('Adaçayı Yeşili', '40')]
    },

    # HIRKA & YELEK
    {
        'title': 'Örgü Dokulu Bej Oversize Hırka',
        'desc': 'Yumuşak triko örgü, geniş salaş kesim düğmesiz bej kadın hırkası.',
        'price': Decimal('549.00'),
        'image': 'products/cardigan.png',
        'category': sub_hirka,
        'variants': [('Bej', 'Standart')]
    },
    {
        'title': 'Lacivert Düğmeli Klasik Erkek Hırka',
        'desc': 'Koyulacivert pamuklu triko, V yaka düğmeli klasik erkek hırka.',
        'price': Decimal('599.00'),
        'image': 'products/cardigan_button_navy.png',
        'category': sub_hirka,
        'seller': seller_fashion,
        'variants': [('Lacivert', 'M'), ('Lacivert', 'L'), ('Lacivert', 'XL')]
    },
    {
        'title': 'Siyah Crop Örgü Kadın Hırka',
        'desc': 'Yüksek bel altlarla uyumlu, crop kesim siyah V yaka düğmeli hırka.',
        'price': Decimal('429.00'),
        'image': 'products/cardigan_crop_black.png',
        'category': sub_hirka,
        'variants': [('Siyah', 'S'), ('Siyah', 'M')]
    },
    {
        'title': 'Pembe Fitilli Crop Triko Hırka',
        'desc': 'Tatlı pembe renkli fitilli triko doku crop stil baharlık hırka.',
        'price': Decimal('399.00'),
        'image': 'products/cardigan_ribbed_pink.png',
        'category': sub_hirka,
        'variants': [('Pembe', 'S'), ('Pembe', 'M')]
    },
    {
        'title': 'Haki Keten Düğmeli Şık Yelek',
        'desc': 'Doğal keten kumaştan üretilmiş, önü düğmeli maskülen kesim haki yelek.',
        'price': Decimal('429.00'),
        'image': 'products/vest_khaki_linen.png',
        'category': sub_hirka,
        'variants': [('Haki', 'S'), ('Haki', 'M'), ('Haki', 'L')]
    },
    {
        'title': 'Siyah Klasik Kesim Düğmeli Yelek',
        'desc': 'Resmi ve şık kombinler için astarlı siyah klasik kumaş yelek.',
        'price': Decimal('449.00'),
        'image': 'products/vest_black_classic.png',
        'category': sub_hirka,
        'variants': [('Siyah', 'S'), ('Siyah', 'M')]
    },
    {
        'title': 'Bej Crop Şık Keten Yelek',
        'desc': 'Yaz modasına uygun, bej keten kumaştan v yaka crop kadın yelek.',
        'price': Decimal('399.00'),
        'image': 'products/vest_beige_crop.png',
        'category': sub_hirka,
        'variants': [('Bej', 'S'), ('Bej', 'M')]
    },

    # PANTOLON & JEAN
    {
        'title': 'Yüksek Bel Mom Fit Açık Mavi Jean Pantolon',
        'desc': '%100 Pamuklu kot kumaşı, yüksek bel rahat mom fit açık mavi jean.',
        'price': Decimal('589.00'),
        'image': 'products/jean_mom_fit_light.png',
        'category': sub_pantolon,
        'variants': [('Açık Mavi', '34'), ('Açık Mavi', '36'), ('Açık Mavi', '38')]
    },
    {
        'title': 'İspanyol Paça Koyu Mavi Denim Pantolon',
        'desc': 'Esnek stretch denim kumaş, paçaya doğru genişleyen ispanyol kesim kot pantolon.',
        'price': Decimal('549.00'),
        'image': 'products/jean_flare_blue.png',
        'category': sub_pantolon,
        'variants': [('Koyu Mavi', '36'), ('Koyu Mavi', '38'), ('Koyu Mavi', '40')]
    },
    {
        'title': 'Düz Kesim Orta Mavi Vintage Jean',
        'desc': 'Zamansız straight fit düz paça orta yıkama denim kot pantolon.',
        'price': Decimal('529.00'),
        'image': 'products/jean_straight_medium.png',
        'category': sub_pantolon,
        'variants': [('Orta Mavi', '36'), ('Orta Mavi', '38'), ('Orta Mavi', '40')]
    },
    {
        'title': 'Geniş Paça Wide-Leg Mavi Jean',
        'desc': 'Dökümlü wide-leg kesim, rahat kullanım sağlayan mavi denim pantolon.',
        'price': Decimal('599.00'),
        'image': 'products/jean_wide_leg_blue.png',
        'category': sub_pantolon,
        'variants': [('Mavi', '36'), ('Mavi', '38')]
    },
    {
        'title': 'Siyah Kumaş Havuç Kesim Pantolon',
        'desc': 'Yüksek bel pileli, dar paça havuç kesim şık siyah kumaş pantolon.',
        'price': Decimal('499.00'),
        'image': 'products/pants_black_tailored.png',
        'category': sub_pantolon,
        'variants': [('Siyah', '36'), ('Siyah', '38'), ('Siyah', '40')]
    },
    {
        'title': 'Siyah Sıkı Kesim Stretch Kot Pantolon',
        'desc': 'Yoğun siyah esnek kumaş, vücudu saran skinny denim pantolon.',
        'price': Decimal('459.00'),
        'image': 'products/pants_black_jean_v2.png',
        'category': sub_pantolon,
        'variants': [('Siyah', '36'), ('Siyah', '38'), ('Siyah', '40')]
    },
    {
        'title': 'Beyaz Keten Rahat Yazlık Pantolon',
        'desc': 'Sıcak havalar için ferah keten dokulu, beli bağcıklı beyaz pantolon.',
        'price': Decimal('529.00'),
        'image': 'products/pants_white_linen.png',
        'category': sub_pantolon,
        'variants': [('Beyaz', 'S'), ('Beyaz', 'M'), ('Beyaz', 'L')]
    },

    # PIJAMA & KOMBİN SETLERİ
    {
        'title': 'California 2li İki İplik Spor Takım',
        'desc': 'Rahat sweatshirt ve eşofman altından oluşan California baskılı spor kombin set.',
        'price': Decimal('649.00'),
        'image': 'products/casual_california_set.png',
        'category': sub_pijama,
        'variants': [('Gri', 'M'), ('Gri', 'L')]
    },
    {
        'title': 'Çiftlere Özel Pamuklu Pijama Seti',
        'desc': '%100 Pamuklu nefes alan ev giyimi pijama kombini.',
        'price': Decimal('589.00'),
        'image': 'products/casual_couple_pajamas.png',
        'category': sub_pijama,
        'variants': [('Desenli', 'M'), ('Desenli', 'L')]
    },
    {
        'title': 'Baba-Oğul Kombin Pamuklu Eşofman Seti',
        'desc': 'Baba ve çocuk için uyumlu pamuklu rahat ev ve yürüyüş takımı.',
        'price': Decimal('699.00'),
        'image': 'products/casual_father_son_set.png',
        'category': sub_pijama,
        'variants': [('Lacivert', 'Standart')]
    },
]

created_count = 0

for item in giyim_items:
    product = Product.objects.create(
        title=item['title'],
        description=item['desc'],
        base_price=item['price'],
        image=item['image'],
        category=item['category'],
        seller=item.get('seller', seller_fashion)
    )
    created_count += 1
    
    for color, size in item['variants']:
        sku_code = f"SKU-GIYIM-{product.id}-{uuid.uuid4().hex[:5].upper()}"
        ProductVariant.objects.create(
            product=product,
            color=color,
            size=size,
            price=item['price'],
            stock=30,
            sku=sku_code
        )

print(f"\nSuccessfully populated Giyim & Moda with {created_count} real products!")
