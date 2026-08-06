import re
from typing import Dict, Any

class DataMaskingService:
    """
    Hassas Kişisel Verilerin (PII - Personally Identifiable Information)
    ve güvenlik bilgilerinin (kredi kartı, telefon, e-posta, adres, şifre)
    loglarda ve arayüzde maskelenmesini sağlayan servis.
    """

    @staticmethod
    def mask_phone(phone: str) -> str:
        """
        Telefon numarasını maskeler.
        Örn: "+905559876543" veya "05559876543" -> "+90 555 *** ** 43"
        """
        if not phone:
            return ""
        digits = re.sub(r'\D', '', str(phone))
        if len(digits) >= 10:
            return f"+90 {digits[1:4]} *** ** {digits[-2:]}" if digits.startswith('0') or digits.startswith('9') else f"{digits[:3]} *** ** {digits[-2:]}"
        return f"{phone[:3]}***{phone[-2:]}" if len(phone) > 5 else "****"

    @staticmethod
    def mask_credit_card(card_number: str) -> str:
        """
        Kredi kartı numarasını maskeler (İlk 4 ve Son 4 hane açık, ortası kapalı).
        Örn: "4543600012345678" -> "4543 **** **** 5678"
        """
        if not card_number:
            return ""
        clean_card = re.sub(r'\D', '', str(card_number))
        if len(clean_card) >= 16:
            return f"{clean_card[:4]} **** **** {clean_card[-4:]}"
        elif len(clean_card) >= 12:
            return f"{clean_card[:4]} **** {clean_card[-4:]}"
        return "**** **** **** ****"

    @staticmethod
    def mask_email(email: str) -> str:
        """
        E-posta adresini maskeler.
        Örn: "bahar.user@example.com" -> "b***r@example.com"
        """
        if not email or '@' not in email:
            return email or ""
        name, domain = email.split('@', 1)
        if len(name) <= 2:
            masked_name = name[0] + "*"
        else:
            masked_name = name[0] + "*" * (len(name) - 2) + name[-1]
        return f"{masked_name}@{domain}"

    @staticmethod
    def mask_address(address: str) -> str:
        """
        Adres detaylarını maskeler.
        Örn: "Atatürk Mah. Ihlamur Sok. No:15 Çankaya / Ankara" -> "A****k M*h. *** Çankaya / Ankara"
        """
        if not address:
            return ""
        words = address.split()
        if len(words) <= 2:
            return f"{words[0][:2]}***"
        masked_words = []
        for i, w in enumerate(words):
            if i == 0 or i == len(words) - 1:
                masked_words.append(w)
            elif len(w) > 3:
                masked_words.append(w[0] + "***")
            else:
                masked_words.append("***")
        return " ".join(masked_words)

    @classmethod
    def mask_dict(cls, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Sözlük içindeki tüm hassas anahtarları (password, card_number, cvv, phone vb.) otomatik maskeler.
        Loglama öncesi veri güvenliği için kullanılır.
        """
        if not isinstance(data, dict):
            return data

        masked_data = {}
        sensitive_keys = {'password', 'confirm_password', 'cvv', 'card_number', 'credit_card', 'secret_key', 'token'}

        for k, v in data.items():
            key_lower = k.lower()
            if key_lower in sensitive_keys:
                masked_data[k] = "********"
            elif 'phone' in key_lower:
                masked_data[k] = cls.mask_phone(str(v))
            elif 'email' in key_lower:
                masked_data[k] = cls.mask_email(str(v))
            elif 'card' in key_lower:
                masked_data[k] = cls.mask_credit_card(str(v))
            elif isinstance(v, dict):
                masked_data[k] = cls.mask_dict(v)
            else:
                masked_data[k] = v

        return masked_data
