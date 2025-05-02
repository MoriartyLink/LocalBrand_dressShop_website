from django.contrib import admin
from .models import Product, ProductVariant, VariantImage, Order, OrderItem

class VariantImageInline(admin.TabularInline):
    model = VariantImage
    extra = 1

class ProductVariantInline(admin.TabularInline):
    model = ProductVariant
    extra = 1
    fields = ('code', 'color', 'size', 'stock', 'price', 'image')

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'brand', 'base_price')
    inlines = [ProductVariantInline]

@admin.register(ProductVariant)
class ProductVariantAdmin(admin.ModelAdmin):
    inlines = [VariantImageInline]
    list_display = ('product', 'code', 'color', 'size', 'stock', 'price')
    search_fields = ('code', 'product__name')


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ['id', 'user', 'total_price', 'status', 'carrier', 'tracking_number', 'created_at']
    list_filter = ['status', 'carrier']
    list_editable = ['status', 'carrier', 'tracking_number']
    inlines = [OrderItemInline]
