# 🛍️ Çoklu Satıcılı (Multi-Vendor) E-Ticaret & İkinci El Pazaryeri Platformu

> **Staj Projesi Değerlendirme & Sunum Dokümanı**  
> Bu proje, Django web çatısı kullanılarak geliştirilmiş, kurumsal standartlarda **Çoklu Satıcılı Pazaryeri (B2C/C2C)**, **Sipariş Bölümleme (Split-Order)**, **Rest API & JWT**, **İkinci El İlan & Teklif Yönetimi** ve **Gelişmiş Analitik Paneller** içeren uçtan uca bir e-ticaret platformudur.

---

## 🌟 Öne Çıkan Sistem Mimarisi ve Özellikler

### 1. 👥 Rol Tabanlı Yetkilendirme (Identity & RBAC)
- **Superadmin (Platform Sahibi):** Satıcı onayları, komisyon oranları (%), kategori ağacı yönetimi, platform kuponları ve platform geneli finansal analiz.
- **Satıcı (Mağaza):** Ürün ve stok varyasyon yönetimi, alt sipariş takibi, mağazaya özel kuponlar, iade/yorum yönetimi ve CSV dışa aktarımı.
- **Müşteri:** Ürün arama/filtreleme, sepet, ödeme, favoriler, teklif verme (C2C), iade talebi, canlı destek ve sipariş takibi.

### 2. 🛒 Akıllı Sipariş Bölümleme (Split Order System)
- Müşterinin sepetindeki farklı satıcılara ait ürünler, ödeme sonrasında otomatik olarak **her satıcıya özel Alt Siparişlere (`SubOrder`)** bölünür.
- Platform komisyonu (`commission_fee`) ve satıcıya aktarılacak net hak ediş (`seller_payout`) otomatik olarak hesaplanır.

### 3. 🏷️ Ürün & Varyasyon Yönetimi
- **Hiyerarşik Kategori Yapısı:** Ebeveyn-Alt Kategori (Parent-Child Subcategories) desteği.
- **Dinamik Varyasyonlar:** Renk, Beden, Numara, Stok ve SKU kodları ile esnek ürün yönetimi.
- **Yorum & Puanlama:** Sadece ürünü satın alıp teslim alan müşterilere **"Doğrulanmış Alıcı (Verified Buyer)"** rozeti verilir.

### 4. 🤝 İkinci El (C2C) İlan & Teklif Sistemi
- Kullanıcıların kendi ikinci el ürünlerini ilana koyabilmesi (Dolap / Sahibinden tarzı).
- İlanlara teklif verme (`submit_offer`), satıcının teklifi onaylama veya reddetme (`respond_offer`) mekanizması.

### 5. 🎯 Sadakat Programı, Kuponlar & Gamification
- **İndirim Kuponları:** Sabit tutar veya yüzdelik indirimler, minimum sepet koşulu ve son kullanma tarihleri.
- **Çarkıfelek (Spin Wheel API):** Günlük çark çevirerek puan veya kupon kazanma.
- **Puan Harcama:** Biriken puanları sepette anlık indirime dönüştürme.

### 6. 📄 Resmî PDF Fatura & Canlı Döviz Kuru
- **ReportLab PDF Engine:** Siparişler için tek tıkla indirilebilen vektörel PDF e-Fatura üretici (`/order/<id>/invoice/pdf/`).
- **Canlı Kur API:** `exchangerate-api` üzerinden anlık kur takibi (TRY/USD/EUR) ve Django Cache önbellekleme.

### 7. 💬 Canlı Sohbet & İnteraktif Analitik Grafikler
- **Yüzen Canlı Chat:** Müşteri ile satıcı arasında anlık mesajlaşma widget'ı.
- **Chart.js Grafikleri:** Satıcı ve Superadmin panellerinde canlı satış eğrileri ve kategori dağılımları.
### 9. 🏆 Kurumsal (Enterprise) Yapay Zeka & B2B Toptan Satış
- **🤖 AI Açıklama Üretici:** Satıcının girdiği ürün başlığından otomatik profesyonel SEO metni ve etiket üretimi (`/api/ai/generate-description/`).
- **🏢 B2B Kademeli Fiyatlandırma:** 10+ adette %15, 50+ adette %30 toptan indirim hesaplayıcı (`/api/b2b/wholesale-pricing/`).
- **📱 Dinamik QR Kod Servisi:** Faturada ve kargo etiketinde orijinallik doğrulama ve kolay iade QR kod üretimi.

### 10. 📊 Satıcı Hakediş Dekontu PDF & Toplu Ürün CSV Yükleme
- **Banka Dekontu PDF:** Satıcı komisyon düşülmüş net hakediş tutarı için resmi PDF dekontu üretimi (`/seller/payout-statement/pdf/`).
- **Toplu Ürün Yükleme:** Satıcıların 100'lerce ürünü tek bir CSV dosyasıyla aktarmasını sağlayan servis ve otomatik CSV şablon indirici (`/seller/download-template/`).

### 12. 🚀 Kurumsal Yeni Eklenen Modüller (Enterprise Enhancements)
- **📦 Gelişmiş İade & Değişim Yönetimi (RMA):** Fotoğraflı iade talebi, onay/kargo süreci ve bakiyenin otomatik iadesi (`/api/returns/create/`).
- **💳 Kullanıcı Cüzdanı & Sanal Bakiye (Wallet System):** Dijital bakiye yükleme, iadelerin cüzdana aktarımı ve bakiye ile alışveriş (`/api/wallet/`).
- **⭐ Satıcı Mağaza Performansı & Rozetler:** Satıcıya özel "Süper Satıcı", "Hızlı Gönderi", "Yüksek Memnuniyet" rozet hesaplayıcı (`/api/seller/<id>/performance/`).
- **⚠️ Stok Hareket Logları & Kritik Stok Uyarısı:** Stok 5 adedin altına düştüğünde anlık bildirim ve stok hareket tablosu (`InventoryLog`).
- **🔍 Trend Arama & Akıllı Otomatik Tamamlama:** Arama terimlerinin analizi, trend kelimeler ve canlı arama tamamlama API'si (`/api/v2/search-autocomplete/`).

### 11. 🚀 Vizyoner Enterprise Modüller (5 Yeni İnovasyon)
- **🤖 AI Stil Kombin Motoru ("Bu Ürünle Harika Gider"):** Ürün sayfasında uyumlu elbiseleri/aksesuarları otomatik kombinleyip *"Tüm Kombini Sepete Ekle"* API'si (`/api/outfit/add-to-cart/`).
- **⚡ Süreli Flaş İndirimler & Canlı Stok Sayacı:** Saatlik geri sayım sayacı ve canlı tükenme progress barı (`🔥 Stokların %85'i Tükendi`).
- **📦 İnteraktif Kargo Takip Zaman Çizelgesi:** Canlı adım adım kargo durum haritası (`/api/cargo-tracking/<order_id>/`).
- **🏆 "PazarClub" Sadakat & Seviye Ödül Sistemi:** Harcama yaptıkça seviye atlama (`Bronz ➔ Gümüş ➔ Altın ➔ Platin`) ve PazarPuan hesabı (`UserLoyalty`).
- **💬 Canlı AI Alışveriş Asistanı Botu ("PazarAsistan"):** Beden tavsiyesi veren ve anında ürün öneren akıllı canlı alışveriş botu (`/api/ai-assistant/`).

### 13. 🎨 Kişiselleştirilebilir Tema & Mikro Animasyonlar
- **🎨 İnteraktif Renk Baloncukları:** Kullanıcının ruh haline göre platform vurgu rengini değiştirebildiği ve tıklama anında ekranında renkli parçacıkların (particle burst) saçıldığı dinamik UX animasyon sistemi.
- **🌙 Gece / Gündüz Modu:** Tek tıkla tüm arayüzü karanlık ve aydınlık moda geçiren yerel hafıza (LocalStorage) senkronizasyonlu tema katmanı.

---

## ⚡ Hızlı Kurulum & Demo Çalıştırma (1-Dakika Guide)

Proje bilgisayarınızda hazır ve aktiftir:
```bash
python manage.py runserver
```
Uygulamaya yerel ortamda **`http://127.0.0.1:8000/`** veya canlı yayında **[https://e-commerce-dkb0.onrender.com/](https://e-commerce-dkb0.onrender.com/)** adresinden erişebilirsiniz.

---

## 🔑 Hazır Test Kullanıcıları (Credentials)

`seed_data` komutu çalıştırıldıktan sonra aşağıdaki hesaplarla sisteme giriş yapabilirsiniz:

| Rol | Kullanıcı Adı | Şifre | Giriş Sayfası / Yetki |
| :--- | :--- | :--- | :--- |
| **Superadmin** | `admin` | `admin123` | `/admin-dashboard/` - Tüm Platform Yönetimi |
| **Satıcı (TeknoDiyarı)** | `tech_seller` | `seller123` | `/seller/` - Elektronik Mağazası |
| **Satıcı (Stil & Moda)** | `fashion_seller` | `seller123` | `/seller/` - Giyim Mağazası |
| **Müşteri 1** | `ahmet_yilmaz` | `customer123` | Mağaza Alışverişi & İki El İlanlar |
| **Müşteri 2** | `ayse_kaya` | `customer123` | Mağaza Alışverişi & Favoriler |

> 📚 **Etkileşimli REST API Dokümantasyonu:** [http://127.0.0.1:8000/api/docs/](http://127.0.0.1:8000/api/docs/)

---

## 🧪 Birim ve Entegrasyon Testleri

Projeye ait tüm servisler, ödeme geçidi, sipariş bölme, kupon, OAuth2/OTP, AI, B2B, Toplu CSV yükleme, RMA İade, Cüzdan, PazarClub, PazarAsistan AI, Kargo Takip ve Kombin Önerici uç noktaları kapsamlı testler ile korunmaktadır.

Testleri çalıştırmak için:
```bash
python manage.py test marketplace
```
> **Test Sonucu:** 69/69 Test Başarılı (`Ran 69 tests - OK`).


---

## 📂 Proje Dizin Yapısı

```
E-commerce/
├── manage.py
├── requirements.txt
├── README.md
├── marketplace_project/      # Django Proje Konfigürasyonu (settings, urls)
└── marketplace/              # Pazaryeri Ana Uygulaması
    ├── models.py             # Veritabanı Modelleri (CustomUser, Product, Order, ReturnRequest, Wallet...)
    ├── views.py              # Web Arayüz View Fonksiyonları
    ├── api_views.py          # REST API & JWT Endpoints
    ├── payment_gateway.py    # Ödeme Geçidi Simülasyonu
    ├── services/             # İş Mantığı Katmanı (Product, Analytics, Return, Wallet, Inventory...)
    ├── management/commands/  # Seed Data Yönetim Komutu
    ├── templates/            # HTML5 & Modern CSS Arayüz Şablonları
    └── tests*.py             # 55 Adet Otomatik Test Dosyası
```

