from marketplace.models import CustomUser

class SocialAuthService:
    """
    Google OAuth2 ve sosyal medya kimlik doğrulama servisi.
    """

    @staticmethod
    def authenticate_google_user(email, name, google_id):
        """
        Google e-posta ve token bilgisine göre kullanıcıyı oturuma alacak CustomUser nesnesini döndürür.
        """
        if not email:
            return None, "E-posta bilgisi bulunamadı."

        username = email.split('@')[0]
        user, created = CustomUser.objects.get_or_create(
            email=email,
            defaults={
                'username': f"g_{username}",
                'role': 'CUSTOMER',
                'first_name': name.split()[0] if name else 'Google',
                'last_name': " ".join(name.split()[1:]) if name and len(name.split()) > 1 else 'Kullanıcısı'
            }
        )

        return user, f"Google ile giriş yapıldı: {user.email}"
