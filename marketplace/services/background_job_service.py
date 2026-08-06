import threading
from concurrent.futures import ThreadPoolExecutor
from typing import Callable, Any

class BackgroundJobService:
    """
    Asenkron Arka Plan Görevleri Yöneticisi (Celery / Background Worker Abstraction).
    Ağır işlemleri (görsel boyutlandırma, e-posta gönderimi, renk analizi, webhook tetikleme)
    ana HTTP istek-yanıt döngüsünü engellemeden (non-blocking) çalıştırır.
    """
    _executor = ThreadPoolExecutor(max_workers=5, thread_name_prefix="PazarYeriWorker")

    @classmethod
    def enqueue_job(cls, func: Callable, *args, **kwargs):
        """
        Herhangi bir Python fonksiyonunu veya metodunu arka plan iş parçacığına gönderir.
        """
        try:
            future = cls._executor.submit(func, *args, **kwargs)
            return future
        except Exception as e:
            print(f"[BackgroundJobService Error] Görev eklenemedi: {e}")
            # Hata durumunda güvenli yedek olarak senkron çağrı
            return func(*args, **kwargs)

    @classmethod
    def process_product_image_async(cls, product_id: int):
        """
        Görsel işleme ve LQIP üretimini asenkron arka planda tetikler.
        """
        def _job():
            from marketplace.models import Product
            from marketplace.services.image_processor_service import ImageProcessorService
            try:
                product = Product.objects.get(id=product_id)
                ImageProcessorService.process_product_image(product)
                print(f"[BackgroundJobService] Ürün #{product_id} görsel optimizasyonu tamamlandı.")
            except Product.DoesNotExist:
                pass
            except Exception as e:
                print(f"[BackgroundJobService Error] Ürün #{product_id} işlenirken hata: {e}")

        return cls.enqueue_job(_job)

    @classmethod
    def send_async_email(cls, subject: str, message: str, recipient_list: list):
        """
        E-posta gönderimini arka planda gerçekleştirir.
        """
        def _job():
            from django.core.mail import send_mail
            try:
                send_mail(
                    subject,
                    message,
                    'noreply@pazaryeri.com',
                    recipient_list,
                    fail_silently=True
                )
                print(f"[BackgroundJobService] E-posta gönderildi: {recipient_list}")
            except Exception as e:
                print(f"[BackgroundJobService Error] E-posta gönderilemedi: {e}")

        return cls.enqueue_job(_job)
