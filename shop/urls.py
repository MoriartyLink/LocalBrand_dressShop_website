from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('shop/', views.shop, name='shop'),
    path('add-to-cart/<int:dress_id>/', views.add_to_cart, name='add_to_cart'),
    path('cart/', views.view_cart, name='view_cart'),
    path('remove-from-cart/<int:dress_id>/', views.remove_from_cart, name='remove_from_cart'),
    path('create-checkout-session/', views.create_checkout_session, name='create_checkout_session'),
]
