from django.core.management.base import BaseCommand
from django.db import transaction
from marketplace.models import CustomUser, SellerProfile, Category, Product, ProductVariant
from decimal import Decimal

class Command(BaseCommand):
    help = "Seeds the database with a massive fashion, cosmetics, jewelry and accessories product catalog."

    def add_arguments(self, parser):
        parser.add_argument(
            '--lorem',
            action='store_true',
            help='Seeds database with loremflickr and 5 main categories with 20 products each.',
        )

    @transaction.atomic
    def handle(self, *args, **kwargs):
        is_lorem = kwargs.get('lorem', False)
        if is_lorem:
            self.stdout.write("Running dynamic loremflickr seeding (5 categories x 20 products)...")
            
            # Clear old products
            from marketplace.models import OrderItem, SubOrder, Order, ReturnRequest, ProductReview, Notification, ChatMessage
            ReturnRequest.objects.all().delete()
            OrderItem.objects.all().delete()
            SubOrder.objects.all().delete()
            Order.objects.all().delete()
            ProductReview.objects.all().delete()
            Notification.objects.all().delete()
            ChatMessage.objects.all().delete()

            ProductVariant.objects.all().delete()
            Product.objects.all().delete()
            Category.objects.all().delete()
            SellerProfile.objects.all().delete()
            CustomUser.objects.exclude(role='SUPERADMIN').delete()
            
            # Create a test seller
            user_seller, _ = CustomUser.objects.get_or_create(
                username="seller_lorem",
                defaults={"email": "lorem_seller@pazaryeri.com", "role": "SELLER"}
            )
            if _:
                user_seller.set_password("seller123")
                user_seller.save()
            seller, _ = SellerProfile.objects.get_or_create(
                user=user_seller,
                defaults={"store_name": "Lorem Butik", "iban": "TR980006200000000012345688"}
            )
            
            categories_def = [
                {"name": "Giyim", "keyword": "clothing"},
                {"name": "Kozmetik", "keyword": "cosmetics"},
                {"name": "Elektronik", "keyword": "electronics"},
                {"name": "Ev", "keyword": "home"},
                {"name": "Aksesuar", "keyword": "accessories"}
            ]
            
            product_templates = {
                "clothing": [
                    "Klasik Kesim Takım Elbise", "Oversize Pamuklu Tişört", "Yüksek Bel Denim Jean", 
                    "Örgü Triko Hırka", "Su Geçirmez Kışlık Mont", "Keten Yazlık Gömlek", 
                    "Desenli Midi Boy Elbise", "Rahat Kesim Kargo Pantolon", "Volanlı Yazlık Etek", 
                    "Klasik Yün Palto"
                ],
                "cosmetics": [
                    "Likit Mat Ruj", "Göz Farı Paleti", "Nemlendirici Yüz Kremi", 
                    "Hacim Veren Maskara", "Kolajen Cilt Serumu", "Kalıcı Çiçeksi Parfüm", 
                    "Doğal Bitkisel Şampuan", "Arındırıcı Kil Maskesi", "Güneş Koruyucu Losyon", 
                    "Canlandırıcı Tonik"
                ],
                "electronics": [
                    "Kablosuz Kulaküstü Kulaklık", "Akıllı Saat Pro", "Bluetooth Taşınabilir Hoparlör", 
                    "Mekanik Oyuncu Klavyesi", "Kablosuz Dikey Mouse", "4K Ultra HD Monitör", 
                    "Hızlı Şarj Güç Bankası", "Full HD Web Kamerası", "Akıllı Ev Güvenlik Kamerası", 
                    "Ergonomik Dizüstü Standı"
                ],
                "home": [
                    "Pamuklu Çift Kişilik Nevresim", "Dekoratif Seramik Vazo", "Kokulu Soya Mumu", 
                    "Örgü Koltuk Şalı", "Ergonomik Ofis Sandalyesi", "Modern Duvar Saati", 
                    "Yumuşak Banyo Paspası Seti", "Dekoratif Duvar Aynası", "Porselen Kahve Fincanı Takımı", 
                    "Metal Ayaklı Lambader"
                ],
                "accessories": [
                    "Hakiki Deri Klasik Cüzdan", "Polarize Güneş Gözlüğü", "Minimalist Çelik Bileklik", 
                    "Gümüş Halka Küpe Takımı", "Paslanmaz Tokalı Deri Kemer", "Klasik Metal Kordon Saat", 
                    "Retro Omuz Çantası", "Su Geçirmez Sırt Çantası", "Minimalist Gümüş Kolye", 
                    "Klasik İpek Fular"
                ]
            }

            unsplash_images = {
                "clothing": [
                    "https://images.unsplash.com/photo-1521572267360-ee0c2909d518?auto=format&fit=crop&w=500&h=500&q=80",
                    "https://images.unsplash.com/photo-1583743814966-8936f5b7be1a?auto=format&fit=crop&w=500&h=500&q=80",
                    "https://images.unsplash.com/photo-1503342217505-b0a15ec3261c?auto=format&fit=crop&w=500&h=500&q=80",
                    "https://images.unsplash.com/photo-1576566588028-4147f3842f27?auto=format&fit=crop&w=500&h=500&q=80",
                    "https://images.unsplash.com/photo-1542272604-787c3835535d?auto=format&fit=crop&w=500&h=500&q=80",
                    "https://images.unsplash.com/photo-1541099649105-f69ad21f3246?auto=format&fit=crop&w=500&h=500&q=80",
                    "https://images.unsplash.com/photo-1582562124811-c09040d0a901?auto=format&fit=crop&w=500&h=500&q=80",
                    "https://images.unsplash.com/photo-1556821840-3a63f95609a7?auto=format&fit=crop&w=500&h=500&q=80",
                    "https://images.unsplash.com/photo-1620799140408-edc6dcb6d633?auto=format&fit=crop&w=500&h=500&q=80",
                    "https://images.unsplash.com/photo-1551028719-00167b16eac5?auto=format&fit=crop&w=500&h=500&q=80",
                    "https://images.unsplash.com/photo-1591047139829-d91aecb6caea?auto=format&fit=crop&w=500&h=500&q=80",
                    "https://images.unsplash.com/photo-1495105787522-5334e3ffa0ef?auto=format&fit=crop&w=500&h=500&q=80",
                    "https://images.unsplash.com/photo-1595777457583-95e059d581b8?auto=format&fit=crop&w=500&h=500&q=80",
                    "https://images.unsplash.com/photo-1585487000160-6ebcfceb0d03?auto=format&fit=crop&w=500&h=500&q=80",
                    "https://images.unsplash.com/photo-1609357605129-26f69add5d6e?auto=format&fit=crop&w=500&h=500&q=80",
                    "https://images.unsplash.com/photo-1561932850-f13404855e53?auto=format&fit=crop&w=500&h=500&q=80",
                    "https://images.unsplash.com/photo-1602573991155-21704f3bd1f6?auto=format&fit=crop&w=500&h=500&q=80",
                    "https://images.unsplash.com/photo-1496747611176-843222e1e57c?auto=format&fit=crop&w=500&h=500&q=80",
                    "https://images.unsplash.com/photo-1539008885128-40d24ee312c9?auto=format&fit=crop&w=500&h=500&q=80",
                    "https://images.unsplash.com/photo-1618244972963-dbee1a7edc95?auto=format&fit=crop&w=500&h=500&q=80"
                ],
                "cosmetics": [
                    "https://images.unsplash.com/photo-1541643600914-78b084683601?auto=format&fit=crop&w=500&h=500&q=80",
                    "https://images.unsplash.com/photo-1592945403244-b3fbafd7f539?auto=format&fit=crop&w=500&h=500&q=80",
                    "https://images.unsplash.com/photo-1594035910387-fea47794261f?auto=format&fit=crop&w=500&h=500&q=80",
                    "https://images.unsplash.com/photo-1586495777744-4413f21062fa?auto=format&fit=crop&w=500&h=500&q=80",
                    "https://images.unsplash.com/photo-1625093742435-6fa192b6fb10?auto=format&fit=crop&w=500&h=500&q=80",
                    "https://images.unsplash.com/photo-1512496015851-a90fb38ba796?auto=format&fit=crop&w=500&h=500&q=80",
                    "https://images.unsplash.com/photo-1522335789203-aabd1fc54bc9?auto=format&fit=crop&w=500&h=500&q=80",
                    "https://images.unsplash.com/photo-1631730359575-38e4755d772b?auto=format&fit=crop&w=500&h=500&q=80",
                    "https://images.unsplash.com/photo-1596462502278-27bfdc403348?auto=format&fit=crop&w=500&h=500&q=80",
                    "https://images.unsplash.com/photo-1617897903246-719242758050?auto=format&fit=crop&w=500&h=500&q=80",
                    "https://images.unsplash.com/photo-1608248597481-496100c80836?auto=format&fit=crop&w=500&h=500&q=80",
                    "https://images.unsplash.com/photo-1515688594390-b649af70d282?auto=format&fit=crop&w=500&h=500&q=80",
                    "https://images.unsplash.com/photo-1601049541289-9b1b7bbbfe19?auto=format&fit=crop&w=500&h=500&q=80",
                    "https://images.unsplash.com/photo-1571781926291-c477ebfd024b?auto=format&fit=crop&w=500&h=500&q=80",
                    "https://images.unsplash.com/photo-1556228720-195a672e8a03?auto=format&fit=crop&w=500&h=500&q=80",
                    "https://images.unsplash.com/photo-1612817288484-6f916006741a?auto=format&fit=crop&w=500&h=500&q=80",
                    "https://images.unsplash.com/photo-1598440947619-2c35fc9aa908?auto=format&fit=crop&w=500&h=500&q=80",
                    "https://images.unsplash.com/photo-1541643600914-78b084683601?auto=format&fit=crop&w=500&h=500&q=80",
                    "https://images.unsplash.com/photo-1535585209827-a15fcdbc4c2d?auto=format&fit=crop&w=500&h=500&q=80",
                    "https://images.unsplash.com/photo-1526947425960-945c6e72858f?auto=format&fit=crop&w=500&h=500&q=80"
                ],
                "electronics": [
                    "https://images.unsplash.com/photo-1505740420928-5e560c06d30e?auto=format&fit=crop&w=500&h=500&q=80",
                    "https://images.unsplash.com/photo-1583394838336-acd977736f90?auto=format&fit=crop&w=500&h=500&q=80",
                    "https://images.unsplash.com/photo-1484704849700-f032a568e944?auto=format&fit=crop&w=500&h=500&q=80",
                    "https://images.unsplash.com/photo-1523275335684-37898b6baf30?auto=format&fit=crop&w=500&h=500&q=80",
                    "https://images.unsplash.com/photo-1508685096489-7aacd43bd3b1?auto=format&fit=crop&w=500&h=500&q=80",
                    "https://images.unsplash.com/photo-1544244015-0df4b3ffc6b0?auto=format&fit=crop&w=500&h=500&q=80",
                    "https://images.unsplash.com/photo-1587829741301-dc798b83add3?auto=format&fit=crop&w=500&h=500&q=80",
                    "https://images.unsplash.com/photo-1615663245857-ac93bb7c39e7?auto=format&fit=crop&w=500&h=500&q=80",
                    "https://images.unsplash.com/photo-1595225476474-87563907a212?auto=format&fit=crop&w=500&h=500&q=80",
                    "https://images.unsplash.com/photo-1601445638532-3c6f6c3aa1d6?auto=format&fit=crop&w=500&h=500&q=80",
                    "https://images.unsplash.com/photo-1527443224154-c4a3942d3acf?auto=format&fit=crop&w=500&h=500&q=80",
                    "https://images.unsplash.com/photo-1560529178-854c8651c6df?auto=format&fit=crop&w=500&h=500&q=80",
                    "https://images.unsplash.com/photo-1618384887929-16ec33fab9ef?auto=format&fit=crop&w=500&h=500&q=80",
                    "https://images.unsplash.com/photo-1547119957-637f8679db1e?auto=format&fit=crop&w=500&h=500&q=80",
                    "https://images.unsplash.com/photo-1542751371-adc38448a05e?auto=format&fit=crop&w=500&h=500&q=80",
                    "https://images.unsplash.com/photo-1625842268584-8f329040ff31?auto=format&fit=crop&w=500&h=500&q=80",
                    "https://images.unsplash.com/photo-1562408590-e32931084e23?auto=format&fit=crop&w=500&h=500&q=80",
                    "https://images.unsplash.com/photo-1555664424-778a1e5e1b48?auto=format&fit=crop&w=500&h=500&q=80",
                    "https://images.unsplash.com/photo-1603481588273-2f908a9a7a1b?auto=format&fit=crop&w=500&h=500&q=80",
                    "https://images.unsplash.com/photo-1616440347437-b1c73416efc2?auto=format&fit=crop&w=500&h=500&q=80"
                ],
                "home": [
                    "https://images.unsplash.com/photo-1513694203232-719a280e022f?auto=format&fit=crop&w=500&h=500&q=80",
                    "https://images.unsplash.com/photo-1586023492125-27b2c045efd7?auto=format&fit=crop&w=500&h=500&q=80",
                    "https://images.unsplash.com/photo-1505691938895-1758d7feb511?auto=format&fit=crop&w=500&h=500&q=80",
                    "https://images.unsplash.com/photo-1583847268964-b28dc8f51f92?auto=format&fit=crop&w=500&h=500&q=80",
                    "https://images.unsplash.com/photo-1538688525198-9b88f6f53126?auto=format&fit=crop&w=500&h=500&q=80",
                    "https://images.unsplash.com/photo-1513519245088-0e12902e5a38?auto=format&fit=crop&w=500&h=500&q=80",
                    "https://images.unsplash.com/photo-1555041469-a586c61ea9bc?auto=format&fit=crop&w=500&h=500&q=80",
                    "https://images.unsplash.com/photo-1532372320978-9b4d7a92b24d?auto=format&fit=crop&w=500&h=500&q=80",
                    "https://images.unsplash.com/photo-1567538096630-e0c55bd6374c?auto=format&fit=crop&w=500&h=500&q=80",
                    "https://images.unsplash.com/photo-1581428982868-e410dd047a90?auto=format&fit=crop&w=500&h=500&q=80",
                    "https://images.unsplash.com/photo-1507089947368-19c1da9775ae?auto=format&fit=crop&w=500&h=500&q=80",
                    "https://images.unsplash.com/photo-1524758631624-e2822e304c36?auto=format&fit=crop&w=500&h=500&q=80",
                    "https://images.unsplash.com/photo-1540518614846-7eded433c457?auto=format&fit=crop&w=500&h=500&q=80",
                    "https://images.unsplash.com/photo-1616486338812-3dadae4b4ace?auto=format&fit=crop&w=500&h=500&q=80",
                    "https://images.unsplash.com/photo-1616046229478-9901c5536a45?auto=format&fit=crop&w=500&h=500&q=80",
                    "https://images.unsplash.com/photo-1617806118233-18e1db207f62?auto=format&fit=crop&w=500&h=500&q=80",
                    "https://images.unsplash.com/photo-1564013799919-ab600027ffc6?auto=format&fit=crop&w=500&h=500&q=80",
                    "https://images.unsplash.com/photo-1615876234886-fd9a39faa97f?auto=format&fit=crop&w=500&h=500&q=80",
                    "https://images.unsplash.com/photo-1616594039964-ae9021a400a0?auto=format&fit=crop&w=500&h=500&q=80",
                    "https://images.unsplash.com/photo-1505693395321-883724634266?auto=format&fit=crop&w=500&h=500&q=80"
                ],
                "accessories": [
                    "https://images.unsplash.com/photo-1584917865442-de89df76afd3?auto=format&fit=crop&w=500&h=500&q=80",
                    "https://images.unsplash.com/photo-1590874103328-eac38a683ce7?auto=format&fit=crop&w=500&h=500&q=80",
                    "https://images.unsplash.com/photo-1594223274512-ad4803739b7c?auto=format&fit=crop&w=500&h=500&q=80",
                    "https://images.unsplash.com/photo-1524592094714-0f0654e20314?auto=format&fit=crop&w=500&h=500&q=80",
                    "https://images.unsplash.com/photo-1522312346375-d1a52e2b99b3?auto=format&fit=crop&w=500&h=500&q=80",
                    "https://images.unsplash.com/photo-1572635196237-14b3f281503f?auto=format&fit=crop&w=500&h=500&q=80",
                    "https://images.unsplash.com/photo-1511499767150-a48a237f0083?auto=format&fit=crop&w=500&h=500&q=80",
                    "https://images.unsplash.com/photo-1627124709703-34b5117f4f67?auto=format&fit=crop&w=500&h=500&q=80",
                    "https://images.unsplash.com/photo-1614179924047-e16494dd20f3?auto=format&fit=crop&w=500&h=500&q=80",
                    "https://images.unsplash.com/photo-1624222247566-5f82406be331?auto=format&fit=crop&w=500&h=500&q=80",
                    "https://images.unsplash.com/photo-1608979148013-8007be4c2a47?auto=format&fit=crop&w=500&h=500&q=80",
                    "https://images.unsplash.com/photo-1598532163257-ae3c6b2524b6?auto=format&fit=crop&w=500&h=500&q=80",
                    "https://images.unsplash.com/photo-1607604276583-eef5d076aa5f?auto=format&fit=crop&w=500&h=500&q=80",
                    "https://images.unsplash.com/photo-1535043934128-cf0b28d52f95?auto=format&fit=crop&w=500&h=500&q=80",
                    "https://images.unsplash.com/photo-1598532213025-58079ed3a2fb?auto=format&fit=crop&w=500&h=500&q=80",
                    "https://images.unsplash.com/photo-1509319117193-57bab727e09d?auto=format&fit=crop&w=500&h=500&q=80",
                    "https://images.unsplash.com/photo-1553062407-98eeb64c6a62?auto=format&fit=crop&w=500&h=500&q=80",
                    "https://images.unsplash.com/photo-1611085583191-a3b1a30a8a3a?auto=format&fit=crop&w=500&h=500&q=80",
                    "https://images.unsplash.com/photo-1522312346375-d1a52e2b99b3?auto=format&fit=crop&w=500&h=500&q=80",
                    "https://images.unsplash.com/photo-1590874103328-eac38a683ce7?auto=format&fit=crop&w=500&h=500&q=80"
                ]
            }

            import random
            for cat_item in categories_def:
                cat = Category.objects.create(name=cat_item["name"])
                keyword = cat_item["keyword"]
                templates = product_templates[keyword]
                img_list = unsplash_images[keyword]
                
                for index in range(1, 21):
                    base_name = templates[(index - 1) % len(templates)]
                    title = f"{base_name} #{index}"
                    price = Decimal(str(random.randint(150, 1500))) + Decimal("0.90")
                    description = f"Harika tasarımı ve yüksek kalitesiyle öne çıkan, günlük kullanıma uygun premium {cat_item['name'].lower()} ürünü."
                    image_url = img_list[index - 1]
                    
                    p = Product.objects.create(
                        seller=seller,
                        category=cat,
                        title=title,
                        base_price=price,
                        image=image_url,
                        description=description
                    )
                    
                    ProductVariant.objects.create(
                        product=p,
                        color=random.choice(["Siyah", "Beyaz", "Gri", "Mavi", "Bej"]),
                        size=random.choice(["S", "M", "L", "XL", "Standart"]),
                        stock=random.randint(10, 100),
                        sku=f"LRM-{keyword[:3].upper()}-{index:02d}"
                    )
            self.stdout.write("Dynamic loremflickr seeding completed successfully!")
            return

        self.stdout.write("Cleaning old products and categories for conversion...")
        
        # Temizleme işlemi
        from marketplace.models import OrderItem, SubOrder, Order, ReturnRequest, ProductReview, Notification, ChatMessage
        ReturnRequest.objects.all().delete()
        OrderItem.objects.all().delete()
        SubOrder.objects.all().delete()
        Order.objects.all().delete()
        ProductReview.objects.all().delete()
        Notification.objects.all().delete()
        ChatMessage.objects.all().delete()

        ProductVariant.objects.all().delete()
        Product.objects.all().delete()
        Category.objects.all().delete()
        SellerProfile.objects.all().delete()
        CustomUser.objects.exclude(role='SUPERADMIN').delete()

        self.stdout.write("Seeding categories and subcategories...")

        # 1. HİYERARŞİK KATEGORİLER
        # 1.1. Giyim & Moda (Level 1)
        cat_moda = Category.objects.create(name="Giyim & Moda")
        
        # Üst Giyim (Level 2)
        cat_ust = Category.objects.create(name="Üst Giyim", parent=cat_moda)
        cat_tisort = Category.objects.create(name="Tişört", parent=cat_ust)
        cat_gomlek = Category.objects.create(name="Gömlek", parent=cat_ust)
        cat_bluz = Category.objects.create(name="Bluz", parent=cat_ust)
        cat_hirka = Category.objects.create(name="Hırka", parent=cat_ust)

        # Alt Giyim (Level 2)
        cat_alt = Category.objects.create(name="Alt Giyim", parent=cat_moda)
        cat_pantolon = Category.objects.create(name="Pantolon", parent=cat_alt)
        cat_jean = Category.objects.create(name="Jean (Kot)", parent=cat_alt)
        cat_etek = Category.objects.create(name="Etek", parent=cat_alt)

        # Dış Giyim (Level 2)
        cat_dis = Category.objects.create(name="Dış Giyim", parent=cat_moda)
        cat_mont = Category.objects.create(name="Mont", parent=cat_dis)
        cat_trenckot = Category.objects.create(name="Trençkot", parent=cat_dis)
        cat_yelek = Category.objects.create(name="Yelek", parent=cat_dis)

        # Elbise ve Tulumlar (Level 2)
        cat_elbise_tulum = Category.objects.create(name="Elbise ve Tulumlar", parent=cat_moda)

        # İç Giyim (Level 2)
        cat_ic = Category.objects.create(name="İç Giyim", parent=cat_moda)
        cat_pijama = Category.objects.create(name="Pijama Grubu", parent=cat_ic)
        cat_atlet = Category.objects.create(name="Atlet & İç Çamaşırı", parent=cat_ic)

        # Kullanım Amacına Göre (Level 2)
        cat_amac = Category.objects.create(name="Kullanım Amacına Göre", parent=cat_moda)
        cat_casual = Category.objects.create(name="Günlük (Casual) Giyim", parent=cat_amac)
        cat_spor_wear = Category.objects.create(name="Spor Giyim", parent=cat_amac)
        cat_formal = Category.objects.create(name="Resmi / İş Giyim", parent=cat_amac)
        cat_party = Category.objects.create(name="Özel Gün ve Gece Giyim", parent=cat_amac)

        # Tarz & Stile Göre (Level 2)
        cat_tarz = Category.objects.create(name="Tarz & Stile Göre", parent=cat_moda)
        cat_klasik = Category.objects.create(name="Klasik Giyim", parent=cat_tarz)
        cat_bohem = Category.objects.create(name="Bohem Giyim", parent=cat_tarz)
        cat_minimalist = Category.objects.create(name="Minimalist Giyim", parent=cat_tarz)
        cat_vintage = Category.objects.create(name="Vintage ve Retro Giyim", parent=cat_tarz)

        # 1.2. Çocuk & Bebek (Level 1)
        cat_cocuk_bebek = Category.objects.create(name="Çocuk & Bebek")
        cat_bebek_giyim = Category.objects.create(name="Bebek Giyim", parent=cat_cocuk_bebek)
        cat_bebek_body = Category.objects.create(name="Bebek Body", parent=cat_bebek_giyim)
        cat_cocuk_takim = Category.objects.create(name="Çocuk Takım", parent=cat_bebek_giyim)
        
        # Temizleme & Banyo (Level 2)
        cat_banyo = Category.objects.create(name="Temizleme & Banyo", parent=cat_cocuk_bebek)
        cat_bebek_sampuan = Category.objects.create(name="Bebek Şampuanı", parent=cat_banyo)
        cat_bebek_losyon = Category.objects.create(name="Bebek Losyonu", parent=cat_banyo)
        cat_bebek_yag = Category.objects.create(name="Bebek Masaj Yağı", parent=cat_banyo)
        cat_bebek_sabun = Category.objects.create(name="Bebek Sabunu", parent=cat_banyo)

        # Cilt Bakımı (Level 2)
        cat_bebek_cilt = Category.objects.create(name="Cilt Bakımı", parent=cat_cocuk_bebek)
        cat_pisik_kremi = Category.objects.create(name="Pişik Kremi", parent=cat_bebek_cilt)
        cat_bebek_yagi = Category.objects.create(name="Bebek Yağı", parent=cat_bebek_cilt)

        # Ağız & Burun (Level 2)
        cat_agiz_burun = Category.objects.create(name="Ağız & Burun", parent=cat_cocuk_bebek)
        cat_serum_fiz = Category.objects.create(name="Serum Fizyolojik", parent=cat_agiz_burun)
        cat_aspirator = Category.objects.create(name="Burun Aspiratörü", parent=cat_agiz_burun)
        cat_dis_fircasi = Category.objects.create(name="Bebek Diş Fırçası", parent=cat_agiz_burun)

        # Tırnak & Saç (Level 2)
        cat_tirnak_sac = Category.objects.create(name="Tırnak & Saç", parent=cat_cocuk_bebek)
        cat_makas = Category.objects.create(name="Bebek Tırnak Makası", parent=cat_tirnak_sac)
        cat_tarak = Category.objects.create(name="Bebek Tarak & Fırça", parent=cat_tirnak_sac)
        cat_bebek_ayakkabi = Category.objects.create(name="Bebek Ayakkabısı", parent=cat_cocuk_bebek)

        # 1.3. Ayakkabı (Yetişkin) (Level 1)
        cat_ayakkabi = Category.objects.create(name="Ayakkabı")
        cat_spor_ayakkabi = Category.objects.create(name="Spor Ayakkabı", parent=cat_ayakkabi)
        cat_klasik_ayakkabi = Category.objects.create(name="Klasik Ayakkabı", parent=cat_ayakkabi)

        # 1.4. Aksesuar, Saat & Gözlük (Level 1) [NEW]
        cat_aksesuar = Category.objects.create(name="Aksesuar & Saat")
        
        # Çanta ve Cüzdan (Level 2)
        cat_canta_cuzdan = Category.objects.create(name="Çanta ve Cüzdan", parent=cat_aksesuar)
        cat_omuz_canta = Category.objects.create(name="Omuz Çantası", parent=cat_canta_cuzdan)
        cat_sirt_canta = Category.objects.create(name="Sırt Çantası", parent=cat_canta_cuzdan)
        cat_cuzdan_kartlik = Category.objects.create(name="Cüzdan & Kartlık", parent=cat_canta_cuzdan)

        # Giyim & Baş Aksesuarları (Level 2)
        cat_bas_aksesuar = Category.objects.create(name="Giyim & Baş Aksesuarları", parent=cat_aksesuar)
        cat_sal_atkı = Category.objects.create(name="Şal & Atkı", parent=cat_bas_aksesuar)
        cat_kemer = Category.objects.create(name="Kemer", parent=cat_bas_aksesuar)
        cat_sapka = Category.objects.create(name="Şapka & Bere", parent=cat_bas_aksesuar)

        # Güneş Gözlüğü ve Saat (Level 2)
        cat_gozluk_saat = Category.objects.create(name="Güneş Gözlüğü ve Saat", parent=cat_aksesuar)
        cat_gunes_gozluk = Category.objects.create(name="Güneş Gözlüğü", parent=cat_gozluk_saat)
        cat_saat = Category.objects.create(name="Saat", parent=cat_gozluk_saat)

        # Saç Aksesuarları (Level 2)
        cat_sac_aksesuar = Category.objects.create(name="Saç Aksesuarları", parent=cat_aksesuar)
        cat_toka = Category.objects.create(name="Tokalar & Lastikler", parent=cat_sac_aksesuar)
        cat_tac = Category.objects.create(name="Taçlar", parent=cat_sac_aksesuar)

        # 1.5. Takılar (Level 1) - Kadın ve Erkek Olarak Ayrıldı
        cat_taki = Category.objects.create(name="Takılar")
        
        # Kadın Takıları (Level 2)
        cat_kadin_taki = Category.objects.create(name="Kadın Takıları", parent=cat_taki)
        cat_kadin_kolye = Category.objects.create(name="Kolye", parent=cat_kadin_taki)
        cat_kadin_yuzuk = Category.objects.create(name="Yüzük", parent=cat_kadin_taki)
        cat_kadin_kupe = Category.objects.create(name="Küpe", parent=cat_kadin_taki)
        cat_kadin_bileklik = Category.objects.create(name="Bileklik", parent=cat_kadin_taki)
        cat_kadin_halhal = Category.objects.create(name="Halhal & Broşlar", parent=cat_kadin_taki)

        # Erkek Takıları (Level 2)
        cat_erkek_taki = Category.objects.create(name="Erkek Takıları", parent=cat_taki)
        cat_erkek_yuzuk = Category.objects.create(name="Yüzük", parent=cat_erkek_taki)
        cat_erkek_bileklik = Category.objects.create(name="Bileklik", parent=cat_erkek_taki)
        cat_erkek_kolye = Category.objects.create(name="Kolye", parent=cat_erkek_taki)
        cat_erkek_kupe = Category.objects.create(name="Küpe", parent=cat_erkek_taki)
        cat_erkek_aksesuar = Category.objects.create(name="Kol Düğmesi & Kravat İğnesi", parent=cat_erkek_taki)

        # 1.6. Kozmetik & Makyaj (Level 1)
        cat_kozmetik = Category.objects.create(name="Kozmetik & Makyaj")
        cat_ruj = Category.objects.create(name="Ruj & Dudak Parlatıcısı", parent=cat_kozmetik)
        cat_far_paleti = Category.objects.create(name="Far Paleti", parent=cat_kozmetik)
        cat_cilt_bakim = Category.objects.create(name="Cilt Bakım Ürünleri", parent=cat_kozmetik)
        cat_makyaj_malzeme = Category.objects.create(name="Makyaj Malzemeleri", parent=cat_kozmetik)
        cat_sac_bakim = Category.objects.create(name="Saç Bakım Ürünleri", parent=cat_kozmetik)
        cat_parfum_deodorant = Category.objects.create(name="Parfüm ve Deodorantlar", parent=cat_kozmetik)
        cat_agiz_bakim = Category.objects.create(name="Ağız Bakım Ürünleri", parent=cat_kozmetik)

        self.stdout.write("- Categories nested ready.")

        # 2. SATICI VE MÜŞTERİ HESAPLARI
        admin_user, _ = CustomUser.objects.get_or_create(
            username="admin",
            defaults={"email": "admin@pazaryeri.com", "role": "SUPERADMIN", "is_superuser": True, "is_staff": True}
        )
        if _:
            admin_user.set_password("admin123")
            admin_user.save()
        
        customer_user, c_created = CustomUser.objects.get_or_create(
            username="customer",
            defaults={"email": "customer@gmail.com", "role": "CUSTOMER"}
        )
        if c_created:
            customer_user.set_password("customer123")
            customer_user.save()

        # Custom sellers based on the user's images
        seller_configs = {
            "titiz_baski": {"store_name": "Titiz Baskı", "email": "info@titizbaski.com", "iban": "TR980006200000000012345671"},
            "hizli_foto": {"store_name": "Hızlı Foto Baskı", "email": "info@hizlifotobaski.com", "iban": "TR980006200000000012345672"},
            "destekar": {"store_name": "destekar", "email": "info@destekar.com", "iban": "TR980006200000000012345673"},
            "serfo": {"store_name": "SERFO Sublimasyon", "email": "info@serfo.com", "iban": "TR980006200000000012345674"},
            "ciceksepeti": {"store_name": "Çiçeksepeti", "email": "info@ciceksepeti.com", "iban": "TR980006200000000012345675"},
            "baskiyap": {"store_name": "Baskiyap.com", "email": "info@baskiyap.com", "iban": "TR980006200000000012345676"},
            "foto_butik": {"store_name": "Foto Butik", "email": "info@fotobutik.com", "iban": "TR980006200000000012345677"},
            "kendin_tasarla": {"store_name": "Kendin Tasarla", "email": "info@kendintasarla.com", "iban": "TR980006200000000012345678"},
            "tasarla_giy": {"store_name": "Tasarla Giy", "email": "info@tasarlagiy.com", "iban": "TR980006200000000012345679"},
            "moda_butik": {"store_name": "Moda Butik", "email": "info@modabutik.com", "iban": "TR980006200000000012345680"},
            "ami_de_coeur": {"store_name": "Ami de Coeur", "email": "info@ami.com", "iban": "TR980006200000000012345681"},
            "genel_markalar": {"store_name": "Genel Markalar", "email": "info@genelmarkalar.com", "iban": "TR980006200000000012345682"},
            "bigdart": {"store_name": "Bigdart", "email": "info@bigdart.com", "iban": "TR980006200000000012345683"},
            "us_polo": {"store_name": "U.S. Polo Assn.", "email": "info@uspolo.com", "iban": "TR980006200000000012345684"},
            "stradivarius": {"store_name": "Stradivarius", "email": "info@stradivarius.com", "iban": "TR980006200000000012345685"},
            "imaj_kuru": {"store_name": "İmaj Kuru Temizleme", "email": "info@imaj.com", "iban": "TR980006200000000012345686"},
            "buenza": {"store_name": "Buenza", "email": "info@buenza.com", "iban": "TR980006200000000012345687"},
            "hatemoglu": {"store_name": "Hatemoğlu", "email": "info@hatemoglu.com", "iban": "TR980006200000000012345688"},
            "sarar": {"store_name": "Sarar", "email": "info@sarar.com", "iban": "TR980006200000000012345689"},
            "nezih_kuru": {"store_name": "Nezih Kuru Temizleme", "email": "info@nezih.com", "iban": "TR980006200000000012345690"},
            "istock": {"store_name": "iStock", "email": "info@istock.com", "iban": "TR980006200000000012345691"},
            "wrangler": {"store_name": "Wrangler", "email": "info@wrangler.com", "iban": "TR980006200000000012345692"},
            "suvari": {"store_name": "Süvari", "email": "info@suvari.com", "iban": "TR980006200000000012345693"},
            "hemington": {"store_name": "Hemington", "email": "info@hemington.com", "iban": "TR980006200000000012345694"},
            "kozmetik_taki": {"store_name": "Kozmetik & Takı Dünyası", "email": "info@kozmetiktaki.com", "iban": "TR980006200000000012345695"},
        }

        sellers = {}
        for username, cfg in seller_configs.items():
            u, created = CustomUser.objects.get_or_create(
                username=username,
                defaults={"email": cfg["email"], "role": "SELLER"}
            )
            if created:
                u.set_password("seller123")
                u.save()
            profile, _ = SellerProfile.objects.get_or_create(
                user=u,
                defaults={"store_name": cfg["store_name"], "iban": cfg["iban"], "commission_rate": 10.00}
            )
            sellers[username] = profile

        # Keep legacy profiles for reference if needed
        seller_a_profile = sellers["moda_butik"]
        seller_b_profile = sellers["kozmetik_taki"]

        # ==========================================
        # 3. GİYİM & MODA SEED VERİLERİ (10'ar Çeşit)
        # ==========================================
        self.stdout.write("Seeding Custom Tişört options...")
        tshirts_data = [
            {"seller": "destekar", "title": "destekar Siyah Erkek Tişört", "price": "199.90", "image": "tshirt_destekar_black.png", "description": "destekar marka premium basic siyah unisex tişört."},
            {"seller": "titiz_baski", "title": "Düz Bisiklet Yaka Mavi Tişört", "price": "180.00", "image": "tshirt_blue_plain.png", "description": "Canlı mavi renk basic bisiklet yaka t-shirt."},
            {"seller": "hizli_foto", "title": "PUBG Fotoğraf Baskılı Beyaz Tişört", "price": "220.00", "image": "tshirt_pubg_white.png", "description": "Yüksek kaliteli PUBG fotoğraf baskılı beyaz pamuklu tişört."},
            {"seller": "moda_butik", "title": "İkili Takım Elbise Baskılı Siyah Tişört", "price": "260.00", "image": "tshirt_suit_black.png", "description": "Özel tasarım ikili takım elbise baskılı siyah bisiklet yaka tişört."},
            {"seller": "ami_de_coeur", "title": "Gün Batımı Manzaralı Turuncu Tişört", "price": "350.00", "image": "tshirt_orange_sunset.png", "description": "Önü gün batımı manzaralı baskılı canlı turuncu t-shirt."}
        ]

        for idx, item in enumerate(tshirts_data):
            p = Product.objects.create(
                seller=sellers[item["seller"]],
                category=cat_tisort,
                title=item["title"],
                base_price=Decimal(item["price"]),
                image=f"products/{item['image']}",
                description=item["description"]
            )
            # Create variants
            color_val = "Beyaz" if "BEYAZ" in item["title"].upper() else ("Mavi" if "MAVİ" in item["title"].upper() else ("Turuncu" if "TURUNCU" in item["title"].upper() else "Siyah"))
            for size in ["S", "M", "L", "XL"]:
                ProductVariant.objects.create(
                    product=p,
                    color=color_val,
                    size=size,
                    stock=50,
                    sku=f"TSH-{idx}-{size}"
                )

        self.stdout.write("Seeding Custom Gömlek options...")
        shirts_data = [
            {"seller": "genel_markalar", "title": "Boyfriend Keten Gömlek - Beyaz", "price": "420.00", "image": "shirt_white_beige_real.png", "description": "Yumuşak keten dokulu, rahat kesim boyfriend beyaz gömlek."},
            {"seller": "bigdart", "title": "3900 Keten Etkili Dökümlü Gömlek - Sarı", "price": "380.00", "image": "shirt_yellow_jeans_real.png", "description": "Keten dokulu dökümlü sarı kadın gömlek."},
            {"seller": "us_polo", "title": "Kruvaze Kesim Keten Gömlek - Saks Mavi", "price": "699.90", "image": "shirt_blue_suit_real.png", "description": "U.S. Polo Assn. kalitesiyle kruvaze kesim saks mavisi gömlek."},
            {"seller": "stradivarius", "title": "Çizgili Oversize Gömlek - Mavi/Beyaz", "price": "550.00", "image": "shirt_striped_white_real.png", "description": "Mavi beyaz dikey çizgili rahat kesim oversize kadın gömlek."},
            {"seller": "buenza", "title": "Klasik Cepli Beyaz Keten Gömlek", "price": "490.00", "image": "shirt_white_close_real.png", "description": "Önü tek cepli, dökümlü keten beyaz kadın gömlek."}
        ]

        for idx, item in enumerate(shirts_data):
            p = Product.objects.create(
                seller=sellers[item["seller"]],
                category=cat_gomlek,
                title=item["title"],
                base_price=Decimal(item["price"]),
                image=f"products/{item['image']}",
                description=item["description"]
            )
            # Create variants
            color_val = "Sarı" if "SARI" in item["title"].upper() else ("Mavi" if "MAVİ" in item["title"].upper() else "Beyaz")
            for size in ["M", "L", "XL"]:
                ProductVariant.objects.create(
                    product=p,
                    color=color_val,
                    size=size,
                    stock=50,
                    sku=f"SH-{idx}-{size}"
                )

        self.stdout.write("Seeding Custom Bluz options...")
        blouses_data = [
            {"seller": "moda_butik", "title": "Deniz Yıldızı Detaylı Boyundan Bağlamalı Beyaz Bluz", "price": "320.00", "image": "blouse_white_starfish.png", "description": "Yaz akşamları ve plaj şıklığı için tasarlanmış, önü deniz yıldızı aksesuarlı boyundan bağlamalı beyaz bluz."},
            {"seller": "moda_butik", "title": "Halter Yaka Canlı Turkuaz Bluz", "price": "280.00", "image": "blouse_turquoise.png", "description": "Yumuşak dökümlü kumaşı ve halter yaka kesimiyle günlük ve şık kombinlerinizin vazgeçilmezi olacak turkuaz bluz."},
            {"seller": "moda_butik", "title": "Deniz Yıldızı Tokalı Beyaz Dik Yaka Bluz", "price": "350.00", "image": "blouse_white_mock_neck.png", "description": "Sol omuz kısmında yer alan altın renkli deniz yıldızı broşuyla modern ve zarif dik yaka kolsuz beyaz bluz."},
            {"seller": "moda_butik", "title": "Degaje Yaka Kolsuz Kahverengi Bluz", "price": "299.90", "image": "blouse_brown_cowl.png", "description": "Dökümlü degaje yakası ve omuz halka detayı ile şıklığı yakalayan saten dokulu kahverengi kolsuz bluz."},
            {"seller": "moda_butik", "title": "Puantiyeli Düşük Omuz Büzgülü Bluz", "price": "340.00", "image": "blouse_polka_dot.png", "description": "Klasik puantiye desenli, asimetrik düşük omuz kesimi ve yan büzgü detaylarıyla hareketlendirilmiş şık bluz."}
        ]

        for idx, item in enumerate(blouses_data):
            p = Product.objects.create(
                seller=sellers[item["seller"]],
                category=cat_bluz,
                title=item["title"],
                base_price=Decimal(item["price"]),
                image=f"products/{item['image']}",
                description=item["description"]
            )
            # Create variants
            color_val = "Beyaz" if "BEYAZ" in item["title"].upper() else ("Turkuaz" if "TURKUAZ" in item["title"].upper() else ("Kahverengi" if "KAHVERENGİ" in item["title"].upper() else "Puantiyeli"))
            for size in ["S", "M", "L"]:
                ProductVariant.objects.create(
                    product=p,
                    color=color_val,
                    size=size,
                    stock=40,
                    sku=f"BLZ-NEW-{idx}-{size}"
                )

        self.stdout.write("Seeding Custom Pantolon options...")
        pants_data = [
            # Set 1 (From Part 2)
            {"seller": "moda_butik", "title": "Beli Bağcıklı Rahat Kesim Beyaz Keten Pantolon", "price": "380.00", "image": "pants_white_linen_v1.png", "description": "Yaz aylarında serin ve rahat hissettiren, beli bağcıklı ve lastikli dökümlü beyaz keten pantolon."},
            {"seller": "moda_butik", "title": "Yüksek Bel Bol Paça Açık Mavi Jean Pantolon", "price": "450.00", "image": "pants_light_blue_jean_v1.png", "description": "Retro esintili bol paça tasarımı ve konforlu yüksek bel kesimiyle açık mavi denim pantolon."},
            {"seller": "moda_butik", "title": "Yüksek Bel Klasik Kumaş Siyah İspanyol Paça Pantolon", "price": "490.00", "image": "pants_black_tailored_v1.png", "description": "İş hayatı ve şık davetler için mükemmel kalıplı, yüksek bel kumaş siyah ispanyol paça pantolon."},
            {"seller": "moda_butik", "title": "Yüksek Bel Bol Paça Siyah Jean Pantolon", "price": "440.00", "image": "pants_black_jean_v1.png", "description": "Kombinlerinize modern ve cool bir hava katacak yüksek bel bol paça siyah denim pantolon."},
            {"seller": "moda_butik", "title": "Mavi Beyaz Çizgili Beli Lastikli Keten Pantolon", "price": "399.90", "image": "pants_striped_casual_v1.png", "description": "Günlük stilinize eşlik edecek, dikey mavi beyaz çizgili ve son derece konforlu beli lastikli keten pantolon."},
            # Set 2 (From current turn)
            {"seller": "moda_butik", "title": "Yüksek Bel Dökümlü Beyaz Kumaş Pantolon", "price": "499.00", "image": "pants_white_linen_v2.png", "description": "Premium dökümlü kumaşı, yüksek bel ve geniş paça kalıbıyla şık beyaz klasik pantolon."},
            {"seller": "moda_butik", "title": "Geniş Paça Eskitme Siyah Denim Jean", "price": "485.00", "image": "pants_black_jean_v2.png", "description": "Rahat kesimi ve eskitilmiş siyah denim dokusuyla sokak modasına uygun modern jean pantolon."},
            {"seller": "moda_butik", "title": "Yüksek Bel Taşlanmış Açık Mavi Mom Jean", "price": "475.00", "image": "pants_light_blue_jean_v2.png", "description": "Konforlu yüksek bel yapısı ve taşlanmış açık mavi rengiyle günlük tarzınıza hitap eden mom jean."},
            {"seller": "moda_butik", "title": "Kuşak Detaylı Yüksek Bel Siyah Kumaş Pantolon", "price": "520.00", "image": "pants_black_tailored_v2.png", "description": "Beli saran tokalı kuşağı ve dökümlü paçalarıyla klasik şıklığı temsil eden siyah kumaş pantolon."},
            {"seller": "moda_butik", "title": "Kemerli Gri İnce Çizgili Klasik Pantolon", "price": "399.90", "image": "pants_striped_casual_v2.png", "description": "Yüksek bel kesimi, şık kemer detayı ve gri ince çizgili klasik deseniyle hem ofis hem günlük kullanım için ideal pantolon."}
        ]

        for idx, item in enumerate(pants_data):
            p = Product.objects.create(
                seller=sellers[item["seller"]],
                category=cat_pantolon,
                title=item["title"],
                base_price=Decimal(item["price"]),
                image=f"products/{item['image']}",
                description=item["description"]
            )
            color_val = "Beyaz" if "BEYAZ" in item["title"].upper() else ("Mavi" if "MAVİ" in item["title"].upper() else ("Siyah" if "SİYAH" in item["title"].upper() else ("Bej" if "BEJ" in item["title"].upper() else ("Camel" if "CAMEL" in item["title"].upper() else "Lacivert"))))
            for size in ["36", "38", "40", "42"]:
                ProductVariant.objects.create(
                    product=p,
                    color=color_val,
                    size=size,
                    stock=25,
                    sku=f"PNT-ALL-{idx}-{size}"
                )

        self.stdout.write("Seeding Custom Etek options...")
        skirts_data = [
            {"seller": "moda_butik", "title": "Leopar Desenli Yırtmaçlı Midi Boy Etek", "price": "340.00", "image": "skirt_leopard.png", "description": "Modern kesimi ve dikkat çekici leopar deseniyle hem şık hem de günlük olarak kombinlenebilen yırtmaçlı midi etek."},
            {"seller": "moda_butik", "title": "Beli Büzgülü Volanlı Beyaz Maxi Etek", "price": "390.00", "image": "skirt_white_flared.png", "description": "Hafif ve nefes alan dokusuyla yaz aylarının vazgeçilmezi olacak dökümlü beyaz maxi etek."},
            {"seller": "moda_butik", "title": "Kruvaze Bağlamalı Siyah Keten Etek", "price": "360.00", "image": "skirt_black_wrap.png", "description": "Kruvaze kesimi ve yandan bağlama detayıyla zarif bir görünüm sunan şık siyah keten etek."},
            {"seller": "moda_butik", "title": "Yıpratma Detaylı Mini Kot Etek", "price": "320.00", "image": "skirt_denim_mini.png", "description": "Yüksek kaliteli denim kumaşı ve hafif yıpratma detaylarıyla spor-şık tarzınızı yansıtacak mini kot etek."},
            {"seller": "moda_butik", "title": "Puantiyeli Yüksek Bel Midi Boy Etek", "price": "350.00", "image": "skirt_polka_dot.png", "description": "Klasik puantiye desenine sahip, dökümlü kumaşı ve konforlu yüksek bel kesimiyle dikkat çeken midi boy etek."}
        ]

        for idx, item in enumerate(skirts_data):
            p = Product.objects.create(
                seller=sellers[item["seller"]],
                category=cat_etek,
                title=item["title"],
                base_price=Decimal(item["price"]),
                image=f"products/{item['image']}",
                description=item["description"]
            )
            color_val = "Leopar" if "LEOPAR" in item["title"].upper() else ("Beyaz" if "BEYAZ" in item["title"].upper() else ("Siyah" if "SİYAH" in item["title"].upper() else ("Mavi" if "KOT" in item["title"].upper() else "Puantiyeli")))
            for size in ["36", "38", "40"]:
                ProductVariant.objects.create(
                    product=p,
                    color=color_val,
                    size=size,
                    stock=25,
                    sku=f"SKT-NEW-{idx}-{size}"
                )

        self.stdout.write("Seeding Custom Jean (Kot) options...")
        jean_data = [
            {"seller": "moda_butik", "title": "Yüksek Bel Bol Paça Mavi Jean Pantolon", "price": "480.00", "image": "jean_wide_leg_blue.png", "description": "Rahat kesimi, yüksek bel yapısı ve dökümlü paçalarıyla günlük şıklığın anahtarı mavi jean pantolon."},
            {"seller": "moda_butik", "title": "Yüksek Bel Mom Fit Açık Mavi Jean Pantolon", "price": "490.00", "image": "jean_mom_fit_light.png", "description": "Vücuda oturan yüksek bel kesimi ve nostaljik mom fit kalıbıyla retro esintili açık mavi jean."},
            {"seller": "moda_butik", "title": "Klasik Düz Kesim Orta Mavi Jean Pantolon", "price": "460.00", "image": "jean_straight_medium.png", "description": "Düz paça tasarımı ve konforlu yapısıyla her mevsim kombinlerinizin kurtarıcısı orta mavi jean."},
            {"seller": "moda_butik", "title": "Düşük Bel İnce Işıltılı Açık Mavi Jean", "price": "540.00", "image": "jean_glitter_light.png", "description": "Yumuşak taşlanmış açık mavi doku üzerinde hafif ışıltı detaylarına sahip, düşük bel bol paça jean."},
            {"seller": "moda_butik", "title": "Yüksek Bel İspanyol Paça Mavi Jean Pantolon", "price": "499.90", "image": "jean_flare_blue.png", "description": "Bacak boyunu uzun gösteren İspanyol paça kesimi ve esnek kumaşıyla vücudu saran şık mavi jean."}
        ]

        for idx, item in enumerate(jean_data):
            p = Product.objects.create(
                seller=sellers[item["seller"]],
                category=cat_jean,
                title=item["title"],
                base_price=Decimal(item["price"]),
                image=f"products/{item['image']}",
                description=item["description"]
            )
            for size in ["36", "38", "40", "42"]:
                ProductVariant.objects.create(
                    product=p,
                    color="Mavi" if "AÇIK MAVİ" not in item["title"].upper() else "Açık Mavi",
                    size=size,
                    stock=25,
                    sku=f"JN-NEW-{idx}-{size}"
                )

        self.stdout.write("Seeding Custom Elbise options...")
        dresses_data = [
            {"seller": "moda_butik", "title": "Kırmızı Çiçek Desenli Kruvaze Yazlık Elbise", "price": "520.00", "image": "dress_red_floral.png", "description": "Kruvaze kesimli, kırmızı üzerine beyaz çiçek desenli son derece şık yazlık midi boy elbise."},
            {"seller": "moda_butik", "title": "Zümrüt Yeşili Saten Askılı Abiye Elbise", "price": "680.00", "image": "dress_emerald_satin.png", "description": "Yumuşak saten dokusu, derin sırt dekoltesi ve göz alıcı zümrüt yeşili rengiyle şık davet elbisesi."},
            {"seller": "moda_butik", "title": "Rahat Kesim Beyaz Keten Plaj Elbisesi", "price": "490.00", "image": "dress_white_linen.png", "description": "Nefes alan keten kumaşı ve dökümlü yapısıyla günlük ve plaj stiline uygun beyaz elbise."},
            {"seller": "moda_butik", "title": "Volanlı Sarı Kruvaze Elbise", "price": "460.00", "image": "dress_yellow_ruffle.png", "description": "Canlı sarı rengi ve omuz/etek volan detaylarıyla hareketlendirilmiş pamuklu yazlık elbise."},
            {"seller": "moda_butik", "title": "Kadife Askılı Yırtmaçlı Siyah Gece Elbisesi", "price": "750.00", "image": "dress_black_velvet.png", "description": "Vücudu saran kadife kumaşı ve zarif bacak yırtmacıyla klasik siyah gece/davet elbisesi."}
        ]

        for idx, item in enumerate(dresses_data):
            p = Product.objects.create(
                seller=sellers[item["seller"]],
                category=cat_elbise_tulum,
                title=item["title"],
                base_price=Decimal(item["price"]),
                image=f"products/{item['image']}",
                description=item["description"]
            )
            for size in ["36", "38", "40"]:
                ProductVariant.objects.create(
                    product=p,
                    color="Kırmızı" if idx==0 else ("Yeşil" if idx==1 else ("Beyaz" if idx==2 else ("Sarı" if idx==3 else "Siyah"))),
                    size=size,
                    stock=20,
                    sku=f"DRS-NEW-{idx}-{size}"
                )

        # Giyim ekstralar
        Product.objects.create(seller=seller_a_profile, category=cat_hirka, title="Örgü Oversize Yumuşak Hırka", base_price=Decimal("650.00"), image="products/cardigan.png").variants.create(color="Bej", size="Standart", stock=15, sku="CLO-HIR-BEJ")

        self.stdout.write("Seeding Custom Hırka options...")
        cardigan_data = [
            {"seller": "moda_butik", "title": "Kapüşonlu Kısa Kesim Siyah Crop Hırka", "price": "350.00", "image": "cardigan_crop_black.png", "description": "Modern spor tarzı, fermuarlı kapüşonlu yapısı ve crop kesimiyle genç ve dinamik siyah hırka."},
            {"seller": "moda_butik", "title": "Oversize Fermuarlı Kapüşonlu Gri Hırka", "price": "480.00", "image": "cardigan_oversize_gray.png", "description": "Geniş kesimi, cepli ve fermuarlı yapısıyla günlük spor şıklığın vazgeçilmezi gri oversize hırka."},
            {"seller": "moda_butik", "title": "Oversize Fermuarlı Kapüşonlu Siyah Hırka", "price": "490.00", "image": "cardigan_oversize_black.png", "description": "Dökümlü ve rahat kalıbı, fermuarlı kapüşonlu tasarımıyla her tarza uyum sağlayan siyah hırka."},
            {"seller": "moda_butik", "title": "Fermuarlı Dik Yaka Fitilli Pembe Hırka", "price": "390.00", "image": "cardigan_ribbed_pink.png", "description": "Vücudu saran fitilli kumaşı, dik yakası ve pratik fermuarlı tasarımıyla tatlı pembe hırka."},
            {"seller": "moda_butik", "title": "V Yaka Klasik Düğmeli Lacivert Hırka", "price": "450.00", "image": "cardigan_button_navy.png", "description": "Yumuşak dokusu, V yaka kesimi ve şık düğmeleriyle klasik tarzı tamamlayan lacivert hırka."}
        ]

        for idx, item in enumerate(cardigan_data):
            p = Product.objects.create(
                seller=sellers[item["seller"]],
                category=cat_hirka,
                title=item["title"],
                base_price=Decimal(item["price"]),
                image=f"products/{item['image']}",
                description=item["description"]
            )
            color_val = "Gri" if "GRİ" in item["title"].upper() else ("Pembe" if "PEMBE" in item["title"].upper() else ("Lacivert" if "LACİVERT" in item["title"].upper() else "Siyah"))
            for size in ["S", "M", "L", "XL"]:
                ProductVariant.objects.create(
                    product=p,
                    color=color_val,
                    size=size,
                    stock=20,
                    sku=f"CRD-NEW-{idx}-{size}"
                )
        
        self.stdout.write("Seeding Custom Mont options...")
        coats_data = [
            {"seller": "moda_butik", "title": "Kapitone Desenli Düğmeli Siyah Uzun Kaban", "price": "1450.00", "image": "coat_black_quilted.png", "description": "Soğuk kış günleri için tasarlanmış, kapitone desenli, düğme kapamalı, şık ve sıcak tutan uzun siyah kaban."},
            {"seller": "moda_butik", "title": "Deri Görünümlü Siyah Şişme Mont", "price": "950.00", "image": "coat_leather_puffer.png", "description": "Modern ve dik yaka kesimi, suni deri dış yüzeyi ile tarzınızı tamamlayacak kısa siyah şişme mont."},
            {"seller": "moda_butik", "title": "İçi Kürklü Süet Kahverengi Havacı Montu", "price": "1250.00", "image": "coat_aviator_brown.png", "description": "İçi komple yumuşak peluş kürk kaplı, fermuarlı ve cepli süet havacı (aviator) stili kahverengi mont."},
            {"seller": "moda_butik", "title": "Oversize Dik Yaka Gri Yün Kaşe Mont", "price": "1100.00", "image": "coat_bomber_gray.png", "description": "Geniş kesimli dökümlü yapısı, minimal tasarımı ve dik yakası ile son derece şık gri yün kaşe mont."},
            {"seller": "moda_butik", "title": "Oversize Boğazlı Siyah Şişme Mont", "price": "980.00", "image": "coat_black_puffer.png", "description": "Ekstra sıcaklık sağlayan yüksek boğazlı yapısı ve hacimli şişme dolgusuyla rahat kesim kısa siyah mont."}
        ]

        for idx, item in enumerate(coats_data):
            p = Product.objects.create(
                seller=sellers[item["seller"]],
                category=cat_mont,
                title=item["title"],
                base_price=Decimal(item["price"]),
                image=f"products/{item['image']}",
                description=item["description"]
            )
            color_val = "Kahverengi" if "KAHVERENGİ" in item["title"].upper() else ("Gri" if "GRİ" in item["title"].upper() else "Siyah")
            for size in ["S", "M", "L", "XL"]:
                ProductVariant.objects.create(
                    product=p,
                    color=color_val,
                    size=size,
                    stock=15,
                    sku=f"COAT-NEW-{idx}-{size}"
                )

        self.stdout.write("Seeding Custom Trençkot options...")
        trench_data = [
            {"seller": "moda_butik", "title": "Kruvaze Kesim Pudra Bej Trençkot", "price": "890.00", "image": "trench_pink_beige.png", "description": "Modern dökümlü kruvaze yaka tasarımı ve hafif yapısıyla mevsim geçişlerinin kurtarıcısı pudra bej trençkot."},
            {"seller": "moda_butik", "title": "Klasik Kemerli Haki Yeşil Trençkot", "price": "950.00", "image": "trench_sage_green.png", "description": "Belden kemerli, arkası rüzgarlıklı ve cepli tasarımıyla yağmurlu ve rüzgarlı havaların şık tamamlayıcısı haki yeşil trençkot."},
            {"seller": "moda_butik", "title": "Oversize Kemerli Acı Kahve Trençkot", "price": "990.00", "image": "trench_dark_brown.png", "description": "Dökümlü oversize kalıbı, derin cepleri ve geniş kemeri ile modern stilinizi öne çıkaracak acı kahve trençkot."},
            {"seller": "moda_butik", "title": "Kısa Kesim Kruvaze Bağlamalı Bej Trençkot", "price": "790.00", "image": "trench_short_beige.png", "description": "Alışılmışın dışında kısa boy tasarımı ve beli saran kuşak detayı ile dinamik ve şık kısa bej trençkot."},
            {"seller": "moda_butik", "title": "Klasik Çift Düğmeli Astarlı Bej Trençkot", "price": "920.00", "image": "trench_classic_beige.png", "description": "Su itici kumaşı, tam boy astarı ve klasik düğme detaylarıyla her dolapta bulunması gereken zamansız bej trençkot."}
        ]

        for idx, item in enumerate(trench_data):
            p = Product.objects.create(
                seller=sellers[item["seller"]],
                category=cat_trenckot,
                title=item["title"],
                base_price=Decimal(item["price"]),
                image=f"products/{item['image']}",
                description=item["description"]
            )
            color_val = "Haki" if "HAKİ" in item["title"].upper() else ("Kahve" if "KAHVE" in item["title"].upper() else "Bej")
            for size in ["S", "M", "L", "XL"]:
                ProductVariant.objects.create(
                    product=p,
                    color=color_val,
                    size=size,
                    stock=20,
                    sku=f"TRN-NEW-{idx}-{size}"
                )

        self.stdout.write("Seeding Custom Yelek options...")
        vest_data = [
            {"seller": "moda_butik", "title": "Klasik Kesim Düğmeli Haki Yeşil Yelek", "price": "390.00", "image": "vest_sage_green.png", "description": "V yaka kesimi, dikiş detayları ve haki yeşil rengiyle maskülen şıklığı yakalayabileceğiniz klasik yelek."},
            {"seller": "moda_butik", "title": "Kısa Kesim Düğmeli Bej Klasik Yelek", "price": "380.00", "image": "vest_beige_crop.png", "description": "Kısa crop kesimi ve önündeki küçük yırtmaç detaylarıyla modern bir tarz sunan şık bej yelek."},
            {"seller": "moda_butik", "title": "V Yaka Klasik Düğmeli Pudra Pembe Yelek", "price": "420.00", "image": "vest_pink_button.png", "description": "Yumuşak tondaki pudra pembe rengi ve konforlu kalıbıyla jean ve kumaş pantolonlarla harika kombinlenen yelek."},
            {"seller": "moda_butik", "title": "V Yaka Düğmeli Klasik Siyah Yelek", "price": "450.00", "image": "vest_black_classic.png", "description": "Her gardırobun olmazsa olmazı, vücuda oturan kesimi ve klasik düğmeleriyle zamansız siyah yele."},
            {"seller": "moda_butik", "title": "Keten Karışımlı Düğmeli Sarı Kolsuz Yelek", "price": "360.00", "image": "vest_yellow_sleeveless.png", "description": "Hafif keten karışımlı kumaşı, yuvarlak yaka kesimi ve pastel sarı tonuyla şık kolsuz yele/bluz."},
            {"seller": "moda_butik", "title": "V Yaka Düğmeli Klasik Beyaz Yelek", "price": "399.90", "image": "vest_white_classic.png", "description": "Modern dikiş detayları, V yaka kesimi ve parlak beyaz rengiyle şık kombinler oluşturabileceğiniz klasik yelek."},
            {"seller": "moda_butik", "title": "V Yaka Düğmeli Klasik Lacivert Yelek", "price": "410.00", "image": "vest_navy_classic.png", "description": "Gövdeyi saran kesimi, şık düğmeleri ve derin lacivert tonuyla iş ve günlük yaşama uygun klasik yelek."},
            {"seller": "moda_butik", "title": "Bisiklet Yaka Düğmeli Acı Kahve Yelek", "price": "370.00", "image": "vest_brown_linen.png", "description": "Keten dokulu kumaşı, bisiklet yakası ve boydan boya düğmeli yapısıyla konforlu kahverengi yelek."},
            {"seller": "moda_butik", "title": "Kemerli Uzun Maskülen Siyah Yelek", "price": "690.00", "image": "vest_long_black.png", "description": "Ceket yakalı, diz boyu uzun kesimi ve beldeki kemer detayıyla son derece şık siyah yele/kaban."},
            {"seller": "moda_butik", "title": "Düğmeli Keten Dokulu Vizon Yelek", "price": "365.00", "image": "vest_khaki_linen.png", "description": "Doğal keten dokulu nefes alan kumaşı, vizon/bej rengiyle yaz ve bahar ayları için ideal şık yelek."}
        ]

        for idx, item in enumerate(vest_data):
            p = Product.objects.create(
                seller=sellers[item["seller"]],
                category=cat_yelek,
                title=item["title"],
                base_price=Decimal(item["price"]),
                image=f"products/{item['image']}",
                description=item["description"]
            )
            color_val = "Haki" if "HAKİ" in item["title"].upper() else ("Bej" if "BEJ" in item["title"].upper() else ("Pembe" if "PEMBE" in item["title"].upper() else ("Sarı" if "SARI" in item["title"].upper() else ("Beyaz" if "BEYAZ" in item["title"].upper() else ("Lacivert" if "LACİVERT" in item["title"].upper() else ("Kahve" if "KAHVE" in item["title"].upper() else ("Vizon" if "VİZON" in item["title"].upper() else "Siyah")))))))
            for size in ["36", "38", "40", "42"]:
                ProductVariant.objects.create(
                    product=p,
                    color=color_val,
                    size=size,
                    stock=20,
                    sku=f"VST-NEW-{idx}-{size}"
                )

        self.stdout.write("Seeding Custom Günlük (Casual) Giyim options...")
        casual_data = [
            {"seller": "moda_butik", "title": "Baba Oğul Kombin Lacivert Tişört Gri Şort Takım", "price": "590.00", "image": "casual_father_son_set.png", "description": "Baba ve oğul için özel olarak hazırlanmış, rahat kesim lacivert pamuklu tişört ve gri şorttan oluşan şık kombin takımı."},
            {"seller": "moda_butik", "title": "İnce Askılı Büzgülü Canlı Sarı Midi Boy Elbise", "price": "480.00", "image": "casual_yellow_dress.png", "description": "Göğüs kısmı esnek gipeli büzgülü, ince omuz askılı, hafif ve dökümlü canlı sarı yazlık midi elbise."},
            {"seller": "moda_butik", "title": "Sevgili Kombini Ufo Baskılı Krem Pijama Takımı", "price": "650.00", "image": "casual_couple_pajamas.png", "description": "Uzun kollu ufo desen baskılı krem üst ve desenli rahat alt pantolondan oluşan, sevgililer için tasarlanmış şık pijama kombini."},
            {"seller": "moda_butik", "title": "İnce Askılı Göz Alıcı Kırmızı Midi Boy Elbise", "price": "490.00", "image": "casual_red_dress.png", "description": "Büzgülü gipeli göğüs detayı ve canlı kırmızı rengiyle yaz günlerinize şıklık katacak askılı pamuklu midi elbise."},
            {"seller": "moda_butik", "title": "California Baskılı Bej Oversize Tişört Şort Takımı", "price": "520.00", "image": "casual_california_set.png", "description": "Oversize rahat kesim bej tişört ve beli lastikli şorttan oluşan, 'California' baskılı şık ve konforlu günlük takım."}
        ]

        for idx, item in enumerate(casual_data):
            p = Product.objects.create(
                seller=sellers[item["seller"]],
                category=cat_casual,
                title=item["title"],
                base_price=Decimal(item["price"]),
                image=f"products/{item['image']}",
                description=item["description"]
            )
            color_val = "Sarı" if "SARI" in item["title"].upper() else ("Kırmızı" if "KIRMIZI" in item["title"].upper() else ("Bej" if "BEJ" in item["title"].upper() else ("Lacivert" if "LACİVERT" in item["title"].upper() else "Krem")))
            for size in ["S", "M", "L", "XL"]:
                ProductVariant.objects.create(
                    product=p,
                    color=color_val,
                    size=size,
                    stock=30,
                    sku=f"CSL-NEW-{idx}-{size}"
                )

        # ==========================================
        # 4. YENİ AKSESUARLAR & SAAT & GÖZLÜK
        # ==========================================
        self.stdout.write("Seeding Çanta, Cüzdan, Kemer, Saat & Gözlük...")
        
        # Omuz Çantası
        bags_data = [
            # 1 Legacy Original Product
            {
                "title": "Hakiki Deri Kadın Omuz Çantası",
                "price": "850.00",
                "image": "bag_shoulder_leather.png",
                "description": "Bölmeli, fermuarlı, geniş hacimli hakiki deri askılı omuz çantası."
            },
            # 5 Shoulder Bags from Batch 1
            {
                "title": "Çok Gözlü Mürdüm Deri Omuz Çantası",
                "price": "350.00",
                "image": "bag_shoulder_maroon.png",
                "description": "Çok fermuarlı, pratik cepleri ve canlı mürdüm rengiyle günlük kullanım için ideal omuz çantası."
            },
            {
                "title": "İkili Set Bej Kadın Omuz ve El Çantası",
                "price": "490.00",
                "image": "bag_shoulder_beige_set.png",
                "description": "Şık bej rengi, geniş iç hacmi ve yanında cüzdan/makyaj çantası olarak kullanabileceğiniz küçük el çantası seti."
            },
            {
                "title": "Calvin Klein Siyah Fermuarlı Omuz Çantası",
                "price": "850.00",
                "image": "bag_shoulder_ck_black.png",
                "description": "Calvin Klein Jeans kabartmalı logolu, fermuarlı bölmesi ve ayarlanabilir askısıyla spor-şık siyah omuz çantası."
            },
            {
                "title": "U.S. Polo Assn. Pudra Klasik Omuz Çantası",
                "price": "690.00",
                "image": "bag_shoulder_uspa_pink.png",
                "description": "U.S. Polo Assn. logolu, zarif pudra tonunda fermuarlı sırt/omuz çantası."
            },
            {
                "title": "Fular Detaylı Siyah Deri Omuz Çantası",
                "price": "420.00",
                "image": "bag_shoulder_black_scarf.png",
                "description": "Askısında leopar desenli şık fular detayı bulunan, geniş ve rahat tasarımlı siyah deri omuz çantası."
            },
            # 5 Shoulder Bags from Batch 2 (New)
            {
                "title": "Siyah, Krem ve Acı Kahve Üçlü Çanta Seti",
                "price": "750.00",
                "image": "bag_shoulder_three_colors.png",
                "description": "Farklı kombinleriniz için siyah, krem ve acı kahve renklerinde şık fular aksesuarlı 3'lü el ve omuz çantası seti."
            },
            {
                "title": "Kroko Desenli Mini Bej El ve Omuz Çantası",
                "price": "320.00",
                "image": "bag_shoulder_mini_beige.png",
                "description": "Minimal tasarımı, kahverengi şık askıları ve taşınabilir boyutlarıyla günlük kullanıma uygun bej omuz çantası."
            },
            {
                "title": "Çok Gözlü Vizon Deri Omuz Çantası",
                "price": "350.00",
                "image": "bag_shoulder_khaki.png",
                "description": "Farklı fermuarlı bölmeleri ve dayanıklı vizon tonuyla günlük eşyalarınızı düzenli taşımanızı sağlayacak omuz çantası."
            },
            {
                "title": "Fularlı Klasik Siyah El ve Omuz Çantası",
                "price": "440.00",
                "image": "bag_shoulder_black_classic_scarf.png",
                "description": "21 cm x 17 cm ideal ebatları, şık siyah-beyaz fular detayı ve asil siyah rengiyle her ortamda şıklık sunan çanta."
            },
            {
                "title": "Yarım Ay Tasarım Siyah Deri Omuz Çantası",
                "price": "380.00",
                "image": "bag_shoulder_half_moon.png",
                "description": "Modern yarım ay (half-moon) kesimi, geniş omuz askısı ve sade siyah rengiyle minimalist tarzın temsilcisi omuz çantası."
            }
        ]

        for idx, item in enumerate(bags_data):
            p = Product.objects.create(
                seller=seller_a_profile,
                category=cat_omuz_canta,
                title=item["title"],
                base_price=Decimal(item["price"]),
                image=f"products/{item['image']}",
                description=item["description"]
            )
            color_val = "Siyah" if "SİYAH" in item["title"].upper() else ("Bej" if "BEJ" in item["title"].upper() else ("Mürdüm" if "MÜRDÜM" in item["title"].upper() else ("Pudra" if "PUDRA" in item["title"].upper() else ("Vizon" if "VİZON" in item["title"].upper() else "Taba"))))
            ProductVariant.objects.create(
                product=p,
                color=color_val,
                size="Standart",
                stock=25,
                sku=f"BAG-SH-ALL-{idx}"
            )

        # Sırt Çantası
        p_sirt = Product.objects.create(
            seller=seller_a_profile, category=cat_sirt_canta, title="Su Geçirmez Laptop Sırt Çantası",
            base_price=Decimal("620.00"), image="products/bag_backpack_tech.png", description="15.6 inç bilgisayar bölmeli, su geçirmez kumaştan sırt çantası."
        )
        ProductVariant.objects.create(product=p_sirt, color="Siyah", stock=40, sku="ACC-BAG-BLK-SRT")

        # Cüzdan & Kartlık
        p_wallet = Product.objects.create(
            seller=seller_a_profile, category=cat_cuzdan_kartlik, title="Mekanizmalı Deri Kartlık Cüzdan",
            base_price=Decimal("280.00"), image="products/accessory_wallet_leather.png", description="Pratik kızak mekanizmalı, RFID korumalı deri minimalist kartlık cüzdan."
        )
        ProductVariant.objects.create(product=p_wallet, color="Taba", stock=100, sku="ACC-WLT-TAB-MKN")

        # Kemer
        p_belt = Product.objects.create(
            seller=seller_a_profile, category=cat_kemer, title="Klasik Dikişli Erkek Deri Kemer",
            base_price=Decimal("240.00"), image="products/accessory_belt_leather.png", description="Kot ve kumaş pantolonlarla uyumlu paslanmaz tokalı hakiki deri kemer."
        )
        ProductVariant.objects.create(product=p_belt, color="Siyah", stock=60, sku="ACC-BLT-BLK")

        # Güneş Gözlüğü
        p_glass = Product.objects.create(
            seller=seller_b_profile, category=cat_gunes_gozluk, title="Polarize Kemik Çerçeve Güneş Gözlüğü",
            base_price=Decimal("450.00"), image="products/accessory_sunglasses_polar.png", description="UV400 korumalı, polarize camlı şık kemik çerçeveli güneş gözlüğü."
        )
        ProductVariant.objects.create(product=p_glass, color="Siyah", stock=80, sku="ACC-GLS-BLK")

        # Yeni Eklenen Güneş Gözlüğü Seçeneği
        p_glass2 = Product.objects.create(
            seller=seller_b_profile, category=cat_gunes_gozluk, title="Klasik Altın Çerçeveli Haki Havacı Gözlüğü",
            base_price=Decimal("590.00"), image="products/accessory_sunglasses_aviator.png", description="UV400 korumalı camları ve dayanıklı altın renkli ince metal çerçevesiyle havacı stili güneş gözlüğü."
        )
        ProductVariant.objects.create(product=p_glass2, color="Altın", stock=15, sku="ACC-GLS-AVTR")

        # Saat (Ersa Saat Benzeri)
        p_watch = Product.objects.create(
            seller=seller_b_profile, category=cat_saat, title="Ersa Saat Premium Çelik Kordon Erkek Kol Saati",
            base_price=Decimal("2400.00"), image="products/accessory_watch_steel.png", description="5 ATM su geçirmez, safir camlı, takvimli premium çelik kol saati."
        )
        ProductVariant.objects.create(product=p_watch, color="Gümüş", stock=15, sku="ACC-WCH-SLV-PREM")

        # Yeni Eklenen Saat Seçenekleri
        p_watch2 = Product.objects.create(
            seller=seller_b_profile, category=cat_saat, title="Klasik Kahverengi Deri Kordonlu Erkek Saat",
            base_price=Decimal("1850.00"), image="products/accessory_watch_leather.png", description="Retro ve şık tasarımıyla öne çıkan, hakiki kahverengi deri kordonlu klasik erkek kol saati."
        )
        ProductVariant.objects.create(product=p_watch2, color="Kahverengi", stock=15, sku="ACC-WCH-BRN-LTHR")

        p_watch3 = Product.objects.create(
            seller=seller_b_profile, category=cat_saat, title="Aktif Ekran Siyah Spor Akıllı Saat",
            base_price=Decimal("2100.00"), image="products/accessory_watch_sport.png", description="Adım sayar, nabız ölçer ve spor modlarına sahip, yüksek çözünürlüklü siyah akıllı saat."
        )
        ProductVariant.objects.create(product=p_watch3, color="Siyah", stock=15, sku="ACC-WCH-BLK-SPR")

        p_watch4 = Product.objects.create(
            seller=seller_b_profile, category=cat_saat, title="Zarif Altın Kaplama Çelik Kadın Saat",
            base_price=Decimal("2850.00"), image="products/accessory_watch_gold.png", description="Özel günler ve günlük şıklık için tasarlanmış, altın sarısı kaplama çelik kordonlu kadın saati."
        )
        ProductVariant.objects.create(product=p_watch4, color="Altın", stock=15, sku="ACC-WCH-GLD-LTHR")

        # Saç Aksesuarları
        p_toka = Product.objects.create(
            seller=seller_b_profile, category=cat_toka, title="5'li Renkli Kadife Mandallı Toka Seti",
            base_price=Decimal("95.00"), image="products/earrings.png", description="Saçları sıkı tutan yumuşak kadife kumaş kaplamalı mandallı toka seti."
        )
        ProductVariant.objects.create(product=p_toka, color="Karışık", stock=200, sku="ACC-TOKA-SET")

        # ==========================================
        # 5. KADIN VE ERKEK TAKILARI
        # ==========================================
        self.stdout.write("Seeding Kadın ve Erkek Takıları...")
        
        # 5.1. Kadın Takıları
        p_k_kolye = Product.objects.create(
            seller=seller_b_profile, category=cat_kadin_kolye, title="Minimalist Zirkon Taşlı Kadın Gümüş Kolye",
            base_price=Decimal("400.00"), image="products/necklace.png", description="925 ayar gümüş zincirli tektaş kadın kolye."
        )
        ProductVariant.objects.create(product=p_k_kolye, color="Gümüş", stock=30, sku="JEW-K-KOL-SILVER")

        p_k_yuzuk = Product.objects.create(
            seller=seller_b_profile, category=cat_kadin_yuzuk, title="Zirkon Taşlı Baget Kadın Altın Yüzük",
            base_price=Decimal("150.00"), image="products/ring.png", description="Ayarlanabilir halkalı baget taşlı altın kadın yüzük."
        )
        ProductVariant.objects.create(product=p_k_yuzuk, color="Altın", stock=80, sku="JEW-K-RNG-GOLD")

        p_k_kupe = Product.objects.create(
            seller=seller_b_profile, category=cat_kadin_kupe, title="Pırlanta Montürlü Gümüş Kadın Küpe Seti",
            base_price=Decimal("250.00"), image="products/earrings.png", description="Yumuşak tırnaklı, parlak gümüş kadın küpe seti."
        )
        ProductVariant.objects.create(product=p_k_kupe, color="Gümüş", stock=45, sku="JEW-K-KUP-SLV")

        # 5.2. Erkek Takıları
        p_e_yuzuk = Product.objects.create(
            seller=seller_b_profile, category=cat_erkek_yuzuk, title="Ay Yıldız Motifli Erkek Gümüş Yüzük",
            base_price=Decimal("380.00"), image="products/jewelry_men_ring.png", description="El işçiliği ay yıldız işlemeli 925 ayar gümüş erkek yüzük."
        )
        ProductVariant.objects.create(product=p_e_yuzuk, color="Gümüş", stock=25, sku="JEW-E-RNG-SLV")

        p_e_aksesuar = Product.objects.create(
            seller=seller_b_profile, category=cat_erkek_aksesuar, title="Çelik Klasik Erkek Kol Düğmesi Seti",
            base_price=Decimal("290.00"), image="products/jewelry_cufflinks_set.png", description="Takım elbiseler için paslanmaz çelik klasik kol düğmesi ve kravat iğnesi seti."
        )
        ProductVariant.objects.create(product=p_e_aksesuar, color="Gümüş/Siyah", stock=50, sku="JEW-E-CUFF-SET")


        # ==========================================
        # 6. BEBEK BAKIM VE SAĞLIK
        # ==========================================
        self.stdout.write("Seeding Bebek Temizlik & Cilt...")
        Product.objects.create(seller=seller_b_profile, category=cat_bebek_sampuan, title="Göz Yakmayan Bebek Şampuanı", base_price=Decimal("140.00"), image="products/shampoo.png").variants.create(size="400ml", stock=80, sku="BABY-BATH-SHAMP")
        Product.objects.create(seller=seller_b_profile, category=cat_bebek_losyon, title="Nemlendirici Bebek Vücut Losyonu", base_price=Decimal("175.00"), image="products/skincare.png").variants.create(size="200ml", stock=90, sku="BABY-BATH-LOTION")
        Product.objects.create(seller=seller_b_profile, category=cat_bebek_yag, title="Rahatlatıcı Bebek Masaj Yağı", base_price=Decimal("195.00"), image="products/perfume.png").variants.create(size="150ml", stock=70, sku="BABY-BATH-OIL")
        Product.objects.create(seller=seller_b_profile, category=cat_pisik_kremi, title="Çinko Oksit Pişik Kremi", base_price=Decimal("150.00"), image="products/skincare.png").variants.create(size="100ml", stock=110, sku="BABY-SKN-CREAM")
        Product.objects.create(seller=seller_b_profile, category=cat_serum_fiz, title="Bebek Serum Fizyolojik (10'lu)", base_price=Decimal("95.00"), image="products/toothpaste.png").variants.create(size="10x5ml", stock=200, sku="BABY-ORL-SALINE")
        Product.objects.create(seller=seller_a_profile, category=cat_bebek_ayakkabi, title="Cırtcırtlı Ortopedik İlk Adım Ayakkabısı", base_price=Decimal("380.00"), image="products/sneakers.png").variants.create(color="Beyaz", size_number=20, stock=20, sku="KID-SH-WHT")

        # ==========================================
        # 8. DYNAMIC PADDING TO 20 PRODUCTS PER CATEGORY
        # ==========================================
        self.stdout.write("Ensuring all leaf categories have at least 20 products with beautiful live images...")
        import random
        from django.utils.text import slugify

        all_categories = Category.objects.all()
        leaf_categories = []
        for cat in all_categories:
            if not cat.subcategories.exists():
                leaf_categories.append(cat)

        def get_specific_keyword(cat_name):
            name = cat_name.lower()
            if "tişört" in name:
                return "tshirt"
            elif "gömlek" in name:
                return "shirt"
            elif "bluz" in name:
                return "blouse"
            elif "hırka" in name:
                return "cardigan"
            elif "trençkot" in name:
                return "trenchcoat"
            elif "jean" in name or "kot" in name:
                return "jeans"
            elif "pantolon" in name:
                return "trousers"
            elif "etek" in name:
                return "skirt"
            elif "mont" in name or "kaban" in name:
                return "coat"
            elif "yelek" in name:
                return "vest"
            elif "elbise" in name or "tulum" in name:
                return "dress"
            elif "pijama" in name or "gece" in name:
                return "pijama"
            elif "atlet" in name or "çamaşır" in name or "iç giyim" in name:
                return "ic_giyim"
            elif "spor" in name:
                return "spor"
            elif "resmi" in name or "klasik" in name:
                return "klasik_giyim"
            elif "bohem" in name or "minimalist" in name or "vintage" in name or "casual" in name or "günlük" in name:
                return "casual"
            elif "bebek" in name or "çocuk" in name:
                return "bebek"
            elif "şampuan" in name or "banyo" in name or "sabun" in name:
                return "banyo"
            elif "cilt" in name or "krem" in name or "losyon" in name or "yağ" in name or "pişik" in name:
                return "skincare"
            elif "ağız" in name or "burun" in name or "serum" in name or "aspiratör" in name:
                return "saglik"
            elif "ruj" in name or "dudak" in name or "far" in name or "makyaj" in name:
                return "makyaj"
            elif "parfüm" in name or "deodorant" in name:
                return "perfume"
            elif "omuz" in name:
                return "handbag"
            elif "sırt" in name:
                return "backpack"
            elif "cüzdan" in name or "kartlık" in name:
                return "wallet"
            elif "kemer" in name:
                return "belt"
            elif "gözlük" in name or "gözlü" in name:
                return "sunglasses"
            elif "saat" in name:
                return "wristwatch"
            elif "kolye" in name or "yüzük" in name or "küpe" in name or "bileklik" in name or "halhal" in name or "takı" in name or "düğme" in name or "toka" in name or "taç" in name:
                return "taki"
            elif "ayakkabı" in name or "sneaker" in name:
                return "sneakers"
            elif "elektronik" in name or "telefon" in name or "bilgisayar" in name:
                return "gadget"
            elif "ev" in name or "dekorasyon" in name or "mobilya" in name:
                return "furniture"
            else:
                return "casual"

        local_pools = {
            "etek": [
                "products/skirt_leopard.png", "products/skirt_white_flared.png",
                "products/skirt_black_wrap.png", "products/skirt_denim_mini.png",
                "products/skirt_polka_dot.png"
            ],
            "pantolon": [
                "products/pants_black_jean_v1.png", "products/pants_black_jean_v2.png",
                "products/pants_black_tailored_v1.png", "products/pants_black_tailored_v2.png",
                "products/pants_light_blue_jean_v1.png", "products/pants_light_blue_jean_v2.png",
                "products/pants_striped_casual_v1.png", "products/pants_striped_casual_v2.png",
                "products/pants_white_linen_v1.png", "products/pants_white_linen_v2.png"
            ],
            "jean": [
                "products/jean_mom_fit_light.png", "products/jean_wide_leg_blue.png",
                "products/jean_straight_medium.png", "products/jean_flare_blue.png",
                "products/jean_glitter_light.png"
            ],
            "elbise": [
                "products/dress_emerald_satin.png", "products/dress_red_floral.png",
                "products/dress_white_linen.png", "products/dress_black_velvet.png",
                "products/dress_yellow_ruffle.png", "products/dress.png"
            ],
            "mont": [
                "products/coat_black_quilted.png", "products/coat_leather_puffer.png",
                "products/coat_aviator_brown.png", "products/coat_black_puffer.png",
                "products/coat_bomber_gray.png", "products/coat.png"
            ],
            "trenchcoat": [
                "products/trench_pink_beige.png", "products/trench_sage_green.png",
                "products/trench_dark_brown.png", "products/trench_classic_beige.png",
                "products/trench_short_beige.png"
            ],
            "yelek": [
                "products/vest_sage_green.png", "products/vest_beige_crop.png",
                "products/vest_pink_button.png", "products/vest_black_classic.png",
                "products/vest_brown_linen.png", "products/vest_khaki_linen.png"
            ],
            "bluz": [
                "products/blouse_white_starfish.png", "products/blouse_turquoise.png",
                "products/blouse_white_mock_neck.png", "products/blouse_brown_cowl.png",
                "products/blouse_polka_dot.png"
            ],
            "hirka": [
                "products/cardigan.png", "products/cardigan_crop_black.png",
                "products/cardigan_oversize_gray.png", "products/cardigan_button_navy.png",
                "products/cardigan_ribbed_pink.png"
            ],
            "gomlek": [
                "products/shirt_white_close_real.png", "products/shirt_white_beige_real.png",
                "products/shirt_yellow_jeans_real.png", "products/shirt_blue_suit_real.png",
                "products/shirt_striped_white_real.png"
            ],
            "tisort": [
                "products/tshirt_blue_plain.png", "products/tshirt_destekar_black.png",
                "products/tshirt_pubg_white.png", "products/tshirt_suit_black.png",
                "products/tshirt_orange_sunset.png"
            ],
            "canta": [
                "products/bag_shoulder_beige_set.png", "products/bag_shoulder_black_classic_scarf.png",
                "products/bag_shoulder_ck_black.png", "products/bag_shoulder_half_moon.png",
                "products/bag_shoulder_khaki.png", "products/bag_backpack_tech.png"
            ],
            "saat": [
                "products/accessory_watch_gold.png", "products/accessory_watch_leather.png",
                "products/accessory_watch_sport.png", "products/accessory_watch_steel.png"
            ],
            "gozluk": [
                "products/accessory_sunglasses_aviator.png", "products/accessory_sunglasses_polar.png"
            ],
            "kemer": [
                "products/accessory_belt_leather.png", "products/accessory_wallet_leather.png"
            ],
            "taki": [
                "products/earrings.png", "products/necklace.png", "products/ring.png",
                "products/jewelry_cufflinks_set.png", "products/jewelry_men_ring.png"
            ],
            "bebek": [
                "products/baby_body.png", "products/baby_shoes_1.jpg", "products/baby_shoes_2.jpg",
                "products/baby_shampoo.jpg", "products/baby_cream.jpg"
            ],
            "kozmetik": [
                "products/lipstick.png", "products/eyeshadow.png", "products/skincare.png",
                "products/perfume.png", "products/shampoo.png"
            ],
            "ayakkabi": [
                "products/sneakers.png", "products/classic_shoes.png", "products/sneakers.jpg"
            ]
        }

        pool_mapping = {
            "tshirt": "tisort", "shirt": "gomlek", "blouse": "bluz", "cardigan": "hirka",
            "trenchcoat": "trenchcoat", "jeans": "jean", "trousers": "pantolon", "skirt": "etek",
            "coat": "mont", "vest": "yelek", "dress": "elbise", "handbag": "canta",
            "backpack": "canta", "wallet": "canta", "belt": "kemer", "sunglasses": "gozluk",
            "wristwatch": "saat", "necklace": "taki", "ring": "taki", "earrings": "taki",
            "bracelet": "taki", "lipstick": "kozmetik", "eyeshadow": "kozmetik",
            "skincare,cream": "kozmetik", "shampoo": "kozmetik", "perfume": "kozmetik",
            "clippers": "kozmetik", "hairpin": "taki", "sneakers": "ayakkabi",
            "gadget": "canta", "furniture": "canta", "pijama": "tisort",
            "ic_giyim": "tisort", "spor": "tisort", "klasik_giyim": "gomlek",
            "casual": "tisort", "bebek": "bebek", "banyo": "kozmetik", "skincare": "kozmetik",
            "saglik": "bebek", "makyaj": "kozmetik", "taki": "taki", "product": "tisort"
        }

        for cat in leaf_categories:
            current_count = Product.objects.filter(category=cat).count()
            if current_count < 20:
                needed = 20 - current_count
                keyword = get_specific_keyword(cat.name)
                pool_name = pool_mapping.get(keyword, "tisort")
                img_pool = local_pools.get(pool_name, local_pools["tisort"])
                self.stdout.write(f"Category '{cat.name}' (keyword: {keyword}, pool: {pool_name}) has {current_count} products, generating {needed} more...")
                for i in range(needed):
                    prefix = random.choice(["Özel Tasarım", "Premium Kalite", "Şık ve Rahat", "Lüks Seri", "Klasik Kesim", "Modern Stil", "Günlük"])
                    title = f"{prefix} {cat.name} Modeli #{current_count + i + 1}"
                    price = Decimal(str(random.randint(120, 1400))) + Decimal(".90")
                    description = f"Yüksek kaliteli malzemeden üretilen, şık tasarımıyla öne çıkan {cat.name.lower()} ürünü."
                    img_path = img_pool[(current_count + i) % len(img_pool)]
                    
                    p = Product.objects.create(
                        seller=seller_a_profile,
                        category=cat,
                        title=title,
                        base_price=price,
                        image=img_path,
                        description=description
                    )
                    ProductVariant.objects.create(
                        product=p,
                        color=random.choice(["Siyah", "Beyaz", "Gri", "Mavi", "Bej"]),
                        size=random.choice(["S", "M", "L", "XL", "Standart"]),
                        stock=random.randint(15, 80),
                        sku=f"AUTO-VRT-{p.id}-{i+1}"
                    )

        self.stdout.write(self.style.SUCCESS("All detailed products and Accessories catalog seeded successfully!"))
