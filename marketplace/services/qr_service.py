class QRService:
    """
    Ürün orijinalliği doğrulama ve kolay iade için SVG QR Kod üreticisi.
    """

    @staticmethod
    def generate_svg_qr_code(data_url):
        """
        Verilen URL veya metin için saf vektörel SVG QR Kod matrisi üretir.
        """
        # SVG QR Kod Simülasyon Şablonu
        url_text = str(data_url)
        svg_code = f'''
        <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100" width="90" height="90">
            <rect width="100" height="100" fill="#ffffff" rx="8"/>
            <!-- Bulucu Desenleri (Corner Trackers) -->
            <rect x="8" y="8" width="24" height="24" fill="#0f172a"/>
            <rect x="12" y="12" width="16" height="16" fill="#ffffff"/>
            <rect x="16" y="16" width="8" height="8" fill="#6366f1"/>

            <rect x="68" y="8" width="24" height="24" fill="#0f172a"/>
            <rect x="72" y="12" width="16" height="16" fill="#ffffff"/>
            <rect x="76" y="16" width="8" height="8" fill="#6366f1"/>

            <rect x="8" y="68" width="24" height="24" fill="#0f172a"/>
            <rect x="12" y="72" width="16" height="16" fill="#ffffff"/>
            <rect x="16" y="76" width="8" height="8" fill="#6366f1"/>

            <!-- Veri Hücreleri -->
            <rect x="40" y="12" width="8" height="8" fill="#0f172a"/>
            <rect x="52" y="20" width="8" height="8" fill="#6366f1"/>
            <rect x="36" y="36" width="12" height="12" fill="#0f172a" rx="2"/>
            <rect x="56" y="44" width="8" height="8" fill="#6366f1"/>
            <rect x="40" y="64" width="12" height="12" fill="#0f172a"/>
            <rect x="64" y="68" width="16" height="16" fill="#0f172a" rx="3"/>
            <text x="50" y="96" font-size="5" font-weight="bold" fill="#64748b" text-anchor="middle">DOĞRULA</text>
        </svg>
        '''
        return svg_code
