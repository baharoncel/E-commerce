# AGENTS.md - Workspace Behavioral Rules

## Güvenlik ve Dokümantasyon Standartları (Security & README First)

1. **Güvenlik Öncelikli Geliştirme (Security-First):**
   - Projenin ilk aşamasından itibaren `SECRET_KEY`, veritabanı parolaları ve API anahtarları asla koda gömülmemeli, `.env` dosyalarında izole edilmelidir.
   - Yetkilendirme (RBAC), CSRF, XSS ve SQL Injection korumaları her modülde sıkı tutulmalı ve kullanıcıya güvenlik önlemleri açıkça açıklanmalıdır.

2. **Zorunlu Kapsamlı README.md Dokümantasyonu:**
   - Her projede, projenin sunumunu ve değerlendirilmesini en üst seviyeye çıkaracak profesyonel bir `README.md` dosyası oluşturulmalıdır.
   - `README.md` içeriğinde: Proje Mimarisi, Özellikler, 1-Dakikalık Kurulum Adımları, Test Kullanıcıları/Şifreleri ve Test Komutları eksiksiz yer almalıdır.

3. **Önce Planla ve Bilgilendir (Propose & Explain First):**
   - Herhangi bir kod değişikliği, yeni dosya veya işlem yapmadan önce yapılacaklar kullanıcıya açık bir şekilde bildirilmeli, ardından uygulamaya geçilmelidir.

4. **Kısa Mesaj & Dosya/Artifact Bazlı Planlama (Token Saver):**
   - Chat penceresinde uzun açıklamalar yerine detaylı planlar dosya (artifact) halinde sunulmalıdır.
   - Chat yanıtları çok kısa tutulmalı, dosya bağlantısı verilip kullanıcıdan direkt onay istenmelidir.

5. **Otomatik Gelecek Adımlar Önerisi (Proactive Next Steps):**
   - Her işlem veya görev tamamlandığında yanıtın sonuna kullanıcı sormak zorunda kalmasın diye otomatik olarak 3-4 adet net, hazır ve uygulamaya geçilebilir 'Bundan Sonra Yapabileceklerimiz' seçeneği eklenmelidir.

