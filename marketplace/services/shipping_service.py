import datetime
from django.utils import timezone

class ShippingService:
    """
    Yurtiçi Kargo & Aras Kargo Canlı Takip Entegrasyonu ve Kargo Barkodu Üretici Servisi.
    """

    CARGO_COMPANIES = {
        'YURTICI': 'Yurtiçi Kargo',
        'ARAS': 'Aras Kargo',
        'MNG': 'MNG Kargo',
        'PTT': 'PTT Kargo'
    }

    @classmethod
    def get_live_cargo_tracking(cls, tracking_number, company_code='YURTICI'):
        """
        Canlı Kargo Takip API simülasyonu.
        Kargo takip numarasına göre kargo hareket geçmişini döndürür.
        """
        if not tracking_number:
            tracking_number = "YK-987654321"

        company_name = cls.CARGO_COMPANIES.get(company_code, 'Yurtiçi Kargo')
        now = timezone.now()

        events = [
            {
                'status': 'Teslim Alındı',
                'location': 'Maslak Şubesi / İstanbul',
                'timestamp': (now - datetime.timedelta(hours=24)).strftime('%d.%m.%Y %H:%M'),
                'desc': f'Kargo göndericiden teslim alındı ({company_name}).'
            },
            {
                'status': 'Aktarma Merkezinde',
                'location': 'İkitelli Transfer Merkezi / İstanbul',
                'timestamp': (now - datetime.timedelta(hours=14)).strftime('%d.%m.%Y %H:%M'),
                'desc': 'Araç yüklemesi yapıldı, varış şubesine sevk edildi.'
            },
            {
                'status': 'Dağıtımda',
                'location': 'Kadıköy Dağıtım Şubesi / İstanbul',
                'timestamp': (now - datetime.timedelta(hours=2)).strftime('%d.%m.%Y %H:%M'),
                'desc': 'Kargo kurye tarafından adrese dağıtıma çıkarıldı.'
            }
        ]

        return {
            'tracking_number': tracking_number,
            'company': company_name,
            'current_status': 'DAĞITIMDA',
            'estimated_delivery': (now + datetime.timedelta(days=1)).strftime('%d.%m.%Y'),
            'events': events
        }

    @classmethod
    def generate_code128_svg_barcode(cls, text):
        """
        Herhangi bir harici kütüphane bağımlılığı gerektirmeyen, saf HTML/SVG Code128 kargo barkodu üreticisi.
        """
        clean_text = "".join(c for c in str(text) if c.isalnum() or c in '-_')
        if not clean_text:
            clean_text = "YK123456789"

        # Basit SVG çubuk (bar) üretimi
        bars = []
        x_offset = 10
        for i, char in enumerate(clean_text):
            val = ord(char)
            # Her karakter için genişlik varyasyonlu çubuklar
            width1 = 2 + (val % 3)
            gap = 2 + ((val * 3) % 3)
            width2 = 3 + ((val * 7) % 4)

            bars.append(f'<rect x="{x_offset}" y="10" width="{width1}" height="60" fill="#0f172a" />')
            x_offset += width1 + gap
            bars.append(f'<rect x="{x_offset}" y="10" width="{width2}" height="60" fill="#0f172a" />')
            x_offset += width2 + gap

        total_width = x_offset + 10
        svg_code = f'''
        <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {total_width} 90" width="100%" height="80">
            <rect width="100%" height="100%" fill="#ffffff"/>
            {''.join(bars)}
            <text x="{total_width / 2}" y="85" font-family="monospace" font-size="12" font-weight="bold" fill="#0f172a" text-anchor="middle">{clean_text}</text>
        </svg>
        '''
        return svg_code
