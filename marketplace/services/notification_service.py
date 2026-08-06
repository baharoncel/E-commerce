import threading
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.conf import settings
from marketplace.models import Notification

class NotificationService:
    """
    Müşterilere ve satıcılara asenkron HTML e-posta ve SMS bildirimi gönderen merkezi servis.
    """

    @staticmethod
    def _send_email_async(subject, recipient_email, html_content):
        def _send():
            try:
                text_content = strip_tags(html_content)
                msg = EmailMultiAlternatives(
                    subject=subject,
                    body=text_content,
                    from_email=getattr(settings, 'DEFAULT_FROM_EMAIL', 'noreply@pazaryeri.com'),
                    to=[recipient_email]
                )
                msg.attach_alternative(html_content, "text/html")
                msg.send(fail_silently=True)
            except Exception as e:
                print(f"[NotificationService Error] E-Posta gönderilemedi: {str(e)}")

        thread = threading.Thread(target=_send)
        thread.daemon = True
        thread.start()

    @staticmethod
    def send_order_confirmation(order):
        """Müşteriye sipariş onay e-postası ve sistem içi bildirim gönderir."""
        if not order.customer.email:
            return

        # 1. Sistem içi bildirim
        Notification.objects.create(
            user=order.customer,
            title="Siparişiniz Alındı",
            message=f"#{order.id} numaralı siparişiniz başarıyla alındı. Toplam tutar: {order.total_amount} TL"
        )

        # 2. HTML E-Posta Gönderimi
        subject = f"PazarYeri - Siparişiniz Alındı (#{order.id})"
        html_content = render_to_string('emails/order_confirmation.html', {'order': order})
        NotificationService._send_email_async(subject, order.customer.email, html_content)

        # 3. SMS & Push Bildirim Simülasyonu
        NotificationService.send_sms(
            order.customer,
            f"Sayin Musterimiz, #{order.id} nolu siparisiniz alinmistir. Toplam: {order.total_amount} TL. Bizi tercih ettiginiz icin tesekkur ederiz."
        )
        NotificationService.send_push_notification(
            order.customer,
            "Siparişiniz Alındı! 🎉",
            f"#{order.id} numaralı siparişiniz başarıyla alındı.",
            {"order_id": order.id, "type": "ORDER_CREATED"}
        )


    @staticmethod
    def send_seller_new_order_alert(sub_order):
        """Satıcıya yeni satış bildirimi e-postası ve sistem içi bildirim gönderir."""
        seller_user = sub_order.seller.user
        
        # 1. Sistem içi bildirim
        Notification.objects.create(
            user=seller_user,
            title="Yeni Satış Bildirimi",
            message=f"Alt Sipariş #{sub_order.id} için mağazanızdan {sub_order.subtotal} TL tutarında sipariş verildi."
        )

        # 2. HTML E-Posta Gönderimi
        if seller_user.email:
            subject = f"Yeni Satış Bildirimi! - Alt Sipariş #{sub_order.id}"
            html_content = render_to_string('emails/seller_new_order.html', {'sub_order': sub_order})
            NotificationService._send_email_async(subject, seller_user.email, html_content)

    @staticmethod
    def send_shipping_update(sub_order):
        """Kargo takip güncellendiğinde müşteriye bilgilendirme gönderir."""
        customer = sub_order.parent_order.customer
        tracking_no = sub_order.parent_order.tracking_number or f"TR-{sub_order.id}98765"

        # 1. Sistem içi bildirim
        Notification.objects.create(
            user=customer,
            title="Kargo Durumu Güncellendi",
            message=f"#{sub_order.parent_order.id} numaralı siparişinizdeki '{sub_order.seller.store_name}' ürünleri kargolandı. Takip No: {tracking_no}"
        )

        # 2. HTML E-Posta Gönderimi
        if customer.email:
            subject = f"Siparişiniz Kargolandı! - #{sub_order.parent_order.id}"
            html_content = render_to_string('emails/shipping_update.html', {
                'sub_order': sub_order,
                'tracking_number': tracking_no
            })
            NotificationService._send_email_async(subject, customer.email, html_content)

        # 3. SMS & Push Bildirimi
        NotificationService.send_sms(
            customer,
            f"Siparisiniz kargolandi! {sub_order.seller.store_name} magazasi urununuz kargoya teslim edildi. Kargo Takip No: {tracking_no}"
        )
        NotificationService.send_push_notification(
            customer,
            "Kargonuz Yola Çıktı! 🚚",
            f"{sub_order.seller.store_name} ürününüz kargolandı. Takip No: {tracking_no}",
            {"order_id": sub_order.parent_order.id, "tracking_number": tracking_no, "type": "SHIPPING_UPDATE"}
        )


    @staticmethod
    def send_return_status_update(return_request):
        """İade talebi sonucu güncelleme bildirimi."""
        customer = return_request.order_item.sub_order.parent_order.customer
        status_display = return_request.get_status_display()

        Notification.objects.create(
            user=customer,
            title="İade Talebi Güncellendi",
            message=f"'{return_request.order_item.product.title}' ürünü için iade talebiniz '{status_display}' olarak güncellendi."
        )

        NotificationService.send_sms(
            customer,
            f"Iade talebiniz hakkinda bilgilendirme: Urun iade talebiniz '{status_display}' durumuna getirilmistir."
        )

    @staticmethod
    def send_sms(user, message):
        """
        SMS Gönderim ve Simülasyon Servisi.
        (Netgsm / Twilio SDK entegrasyon noktası).
        """
        print(f"[SMS Gateway -> {user.username}]: {message}")

    @staticmethod
    def send_push_notification(user, title, body, data_payload=None):
        """
        Mobil cihazlara (FCM / APNS) Anlık Telefon Bildirimi (Push Notification) Gönderici.
        """
        from marketplace.models import PushDeviceToken
        tokens = PushDeviceToken.objects.filter(user=user)
        if not tokens.exists():
            print(f"[Push Dispatcher] {user.username} için kayıtlı mobil cihaz token'ı bulunamadı.")
            return

        for t in tokens:
            print(f"[Push Dispatcher -> {t.device_type} ({t.token[:12]}...)]: 📱 [{title}] {body} | Payload: {data_payload or {}}")

    @staticmethod
    def send_low_stock_alert(seller_user, product_title, current_stock):
        """
        Satıcıya ürün stok seviyesi kritik sınırı (5 adet) altına düştüğünde uyarı gönderir.
        """
        title = "⚠️ Kritik Stok Uyarısı"
        message = f"'{product_title}' ürününüzün stoku kritik seviyeye ulaştı! Kalan Stok: {current_stock} adet."

        Notification.objects.create(
            user=seller_user,
            title=title,
            message=message
        )

        if seller_user.email:
            subject = f"Kritik Stok Uyarısı! - {product_title}"
            html_content = f"<div style='font-family:sans-serif;'><h2>Kritik Stok Uyarısı</h2><p>{message}</p><p>Lütfen en kısa sürede stok güncellemesi yapınız.</p></div>"
            NotificationService._send_email_async(subject, seller_user.email, html_content)

        NotificationService.send_sms(seller_user, message)


