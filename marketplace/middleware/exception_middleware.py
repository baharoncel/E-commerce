import logging
import traceback
from django.http import JsonResponse, HttpResponseServerError
from django.shortcuts import render
from marketplace.services.data_masking_service import DataMaskingService

logger = logging.getLogger('pazaryeri')

class CentralizedExceptionMiddleware:
    """
    Merkezi Hata Yönetimi ve Güvenlik Loglama Middleware'i.
    Yakalanmayan istisnaları (Unhandled Exceptions) yakalar,
    hassas verileri maskeler, stack trace bilgilerini 'logs/pazaryeri.log'
    dosyasına kaydeder ve kullanıcıya güvenli hata ekranı döndürür.
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        return self.get_response(request)

    def process_exception(self, request, exception):
        # 1. İstemci ve İstek Bilgilerini Derle
        client_ip = request.META.get('HTTP_X_FORWARDED_FOR', request.META.get('REMOTE_ADDR', '127.0.0.1'))
        user_obj = getattr(request, 'user', None)
        user_info = f"User #{user_obj.id} ({user_obj.username})" if user_obj and getattr(user_obj, 'is_authenticated', False) else "AnonymousUser"
        
        # Post/Get verilerini maskele
        raw_data = request.POST.dict() if request.method == 'POST' else request.GET.dict()
        masked_data = DataMaskingService.mask_dict(raw_data)

        # 2. Yapılandırılmış Hata Logu Oluştur
        log_msg = (
            f"[CENTRALIZED EXCEPTION HANDLER]\n"
            f"Path: {request.method} {request.path}\n"
            f"Client IP: {client_ip}\n"
            f"User: {user_info}\n"
            f"Masked Parameters: {masked_data}\n"
            f"Exception Type: {type(exception).__name__}: {str(exception)}\n"
            f"Traceback:\n{traceback.format_exc()}"
        )
        logger.error(log_msg)

        # 3. İstemci Tipine Göre Güvenli Hata Yanıtı Döndür
        if request.path.startswith('/api/') or request.headers.get('Accept') == 'application/json':
            return JsonResponse({
                'success': False,
                'message': 'Sunucuda beklenmeyen bir hata oluştu. Lütfen tekrar deneyiniz.',
                'error_code': 500,
                'errors': [str(exception)] if logger.isEnabledFor(logging.DEBUG) else None
            }, status=500)

        # HTML İstemcileri İçin Güvenli 500 Sayfası
        return HttpResponseServerError(
            '<div style="font-family: sans-serif; text-align: center; padding: 4rem;">'
            '<h1 style="color: #e63946;">500 - Sunucu Hatası</h1>'
            '<p style="color: #666;">İsteğiniz işlenirken teknik bir aksaklık meydana geldi. Sistem yöneticilerimiz bilgilendirildi.</p>'
            '<a href="/" style="display: inline-block; margin-top: 1rem; padding: 0.6rem 1.2rem; background: #1d3557; color: white; border-radius: 6px; text-decoration: none;">Ana Sayfaya Dön</a>'
            '</div>'
        )
