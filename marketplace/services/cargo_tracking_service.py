"""
Cargo Tracking Service & Shipment Timeline Generator
"""
from datetime import timedelta
from django.utils import timezone

STATUS_TIMELINE = [
    {"code": "PENDING", "title": "Sipariş Alındı", "icon": "fa-solid fa-file-invoice", "desc": "Siparişiniz satıcıya iletildi."},
    {"code": "PROCESSING", "title": "Hazırlanıyor", "icon": "fa-solid fa-box-open", "desc": "Ürününüz paketleniyor ve faturası kesiliyor."},
    {"code": "SHIPPED", "title": "Kargoya Verildi", "icon": "fa-solid fa-truck-fast", "desc": "Kargo kuryesine teslim edildi. Yolda."},
    {"code": "DELIVERED", "title": "Teslim Edildi", "icon": "fa-solid fa-house-circle-check", "desc": "Sipariş başarıyla teslim edildi."},
]

def get_order_tracking_timeline(order):
    """
    Computes visual progress timeline and estimated delivery for an Order or SubOrder.
    """
    current_status = getattr(order, 'order_status', None) or getattr(order, 'status', 'RECEIVED')
    created_at = getattr(order, 'created_at', timezone.now())

    current_step_index = 0
    if current_status == 'PREPARING' or current_status == 'PROCESSING':
        current_step_index = 1
    elif current_status == 'SHIPPED':
        current_step_index = 2
    elif current_status == 'DELIVERED':
        current_step_index = 3


    timeline = []
    for idx, step in enumerate(STATUS_TIMELINE):
        step_copy = step.copy()
        if idx < current_step_index:
            step_copy["state"] = "completed"
        elif idx == current_step_index:
            step_copy["state"] = "current"
        else:
            step_copy["state"] = "pending"
        timeline.append(step_copy)

    estimated_delivery = created_at + timedelta(days=2)
    tracking_code = getattr(order, 'tracking_code', None) or f"TR-{order.id}9824"

    return {
        "order_id": order.id,
        "current_status": current_status,
        "current_step_index": current_step_index,
        "timeline": timeline,
        "estimated_delivery_date": estimated_delivery.strftime("%d.%m.%Y"),
        "tracking_code": tracking_code,
        "cargo_company": "Yurtiçi Kargo (Express)",
    }
