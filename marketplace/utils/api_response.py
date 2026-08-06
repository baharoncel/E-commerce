from django.http import JsonResponse
from django.utils import timezone
from typing import Any, Optional

class ApiResponse:
    """
    RESTful API Standart Yanıt Zarfı (Envelope Standardizer).
    Mobil (iOS/Android) ve Frontend uygulamalarının tutarlı JSON almasını sağlar.
    """

    @staticmethod
    def success(data: Any = None, message: str = "İşlem başarılı.", status: int = 200) -> JsonResponse:
        payload = {
            "success": True,
            "message": message,
            "data": data,
            "errors": None,
            "timestamp": timezone.now().isoformat()
        }
        return JsonResponse(payload, status=status)

    @staticmethod
    def error(message: str = "İşlem başarısız.", errors: Any = None, status: int = 400) -> JsonResponse:
        payload = {
            "success": False,
            "message": message,
            "data": None,
            "errors": errors,
            "timestamp": timezone.now().isoformat()
        }
        return JsonResponse(payload, status=status)

    @staticmethod
    def unauthorized(message: str = "Yetkisiz erişim. Geçerli JWT token gerekli.") -> JsonResponse:
        return ApiResponse.error(message=message, status=401)

    @staticmethod
    def not_found(message: str = "Aranan kaynak bulunamadı.") -> JsonResponse:
        return ApiResponse.error(message=message, status=404)
