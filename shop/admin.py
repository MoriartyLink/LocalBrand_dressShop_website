from django.conf import settings
from django.contrib import  admin
from django.core.mail import send_mail

from .models import Dress
from .models import Order, OrderItem


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0

class OrderAdmin(admin.ModelAdmin):
    list_display = ['id', 'user', 'total_price', 'status', 'carrier', 'tracking_number', 'created_at']
    list_filter = ['status', 'carrier', 'created_at']
    inlines = [OrderItemInline]
    list_editable = ['status', 'carrier', 'tracking_number']

    def save_model(self, request, obj, form, change):
        if change:
            old_order = Order.objects.get(pk=obj.pk)
            if old_order.status != obj.status and obj.status == 'shipped':
                if obj.user and obj.user.email:
                    # 📧 Include tracking info
                    message = f"Hi {obj.user.username},\n\n" \
                              f"Good news! Your order #{obj.id} has been shipped.\n\n"
                    if obj.tracking_number:
                        message += f"Tracking Number: {obj.tracking_number}\n"
                        if obj.carrier:
                            message += f"Carrier: {obj.get_carrier_display()}\n"
                    message += "\nIt will be delivered soon.\n\nThanks for shopping with us!\nLocal Brand Shop"

                    send_mail(
                        subject='Your Order Has Been Shipped! 🚚',
                        message=message,
                        from_email=settings.EMAIL_HOST_USER,
                        recipient_list=[obj.user.email],
                        fail_silently=False,
                    )
        super().save_model(request, obj, form, change)

admin.site.register(Dress)
admin.site.register(Order,OrderAdmin)
admin.site.register(OrderItem)