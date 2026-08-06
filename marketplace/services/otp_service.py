import random
from django.core.cache import cache
from marketplace.models import CustomUser

class OTPService:
    """
    Telefon numarası ile SMS OTP tek kullanımlık şifre doğrulama servisi.
    """
    
    @staticmethod
    def generate_otp(phone_number):
        """
        Verilen telefon numarası için 6 haneli rastgele OTP kodu üretir ve 5 dakika saklar.
        """
        clean_phone = "".join(filter(str.isdigit, str(phone_number)))
        otp_code = f"{random.randint(100000, 999999)}"
        cache_key = f"otp_code_{clean_phone}"
        cache.set(cache_key, otp_code, 300) # 5 dakika geçerli
        
        # SMS Gönderim Simülasyonu
        print(f"📱 [SMS OTP Gateway -> +90{clean_phone}]: Giriş Kodu: {otp_code} (5 dakika geçerlidir).")
        return otp_code, clean_phone

    @staticmethod
    def verify_otp_and_login(phone_number, otp_code):
        """
        Girilmiş OTP kodunu doğrular, eşleşirse kullanıcıyı getirir veya yeni müşteri oluşturur.
        """
        clean_phone = "".join(filter(str.isdigit, str(phone_number)))
        cache_key = f"otp_code_{clean_phone}"
        stored_code = cache.get(cache_key)

        # Demo kolaylığı için '123456' veya üretilen kod kabul edilir
        if not stored_code and otp_code != '123456':
            return False, "OTP kodunun süresi dolmuş veya geçersiz.", None

        if stored_code == str(otp_code) or str(otp_code) == '123456':
            cache.delete(cache_key)
            username = f"user_{clean_phone}"
            
            user, created = CustomUser.objects.get_or_create(
                username=username,
                defaults={
                    'email': f"{clean_phone}@pazar.com",
                    'role': 'CUSTOMER',
                    'first_name': 'Mobil',
                    'last_name': 'Müşteri'
                }
            )
            return True, "Telefon doğrulaması başarılı!", user

        return False, "Hatalı doğrulama kodu!", None
