from django.contrib import admin
from .models import Product, ProductVariant, ProductImage, VariantImage, Order, OrderItem

class ProductImageInline(admin.TabularInline):
    model = ProductImage
    extra = 1

class ProductVariantInline(admin.TabularInline):
    model = ProductVariant
    extra = 1

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('code', 'name', 'brand', 'base_price')
    inlines = [ProductImageInline, ProductVariantInline]

class VariantImageInline(admin.TabularInline):
    model = VariantImage
    extra = 1

@admin.register(ProductVariant)
class ProductVariantAdmin(admin.ModelAdmin):
    inlines = [VariantImageInline]
    list_display = ('product', 'color', 'size', 'stock')

class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ['id', 'user', 'total_price', 'status', 'carrier', 'tracking_number', 'created_at']
    list_filter = ['status', 'carrier']
    list_editable = ['status', 'carrier', 'tracking_number']
    inlines = [OrderItemInline]
