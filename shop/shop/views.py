import stripe
import stripe
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.db.models import Sum
from django.urls import reverse
from django.views.decorators.csrf import csrf_exempt
from .models import Product, ProductVariant
from django.core.mail import send_mail
from django.contrib.auth.decorators import login_required
from .models import Order
from .models import ProductVariant, Order, OrderItem
from django.contrib.auth.decorators import login_required

from django.conf import settings
from django.http import JsonResponse
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth import login as auth_login, authenticate, logout as auth_logout
from django.shortcuts import render, redirect
from django.contrib import messages

stripe.api_key = settings.STRIPE_SECRET_KEY

def home(request):
    products = Product.objects.all()
    for product in products:
        product.total_stock = product.variants.aggregate(total=Sum('stock'))['total'] or 0
    return render(request, 'shop/home.html', {'products': products})

def shop(request):
    products = Product.objects.all()
    for product in products:
        product.total_stock = product.variants.aggregate(total=Sum('stock'))['total'] or 0
    return render(request, 'shop/shop.html', {'products': products})

def product_detail(request, product_id):
    product = get_object_or_404(Product, pk=product_id)
    default_variant = product.variants.first()
    sizes = product.variants.values_list('size', flat=True).distinct()
    return render(request, 'shop/product_detail.html', {
        'product': product,
        'default_variant': default_variant,
        'sizes': sizes
    })

def add_to_cart(request, product_id):
    if request.method == 'POST':
        variant_id = request.POST.get('variant_id')
        if not variant_id:
            messages.error(request, "Please select a variant.")
            return redirect('product_detail', product_id=product_id)

        cart = request.session.get('cart', {})

        if variant_id in cart:
            cart[variant_id]['quantity'] += 1
        else:
            cart[variant_id] = {
                'quantity': 1,
                'product_id': product_id
            }

        request.session['cart'] = cart
        messages.success(request, "Item added to cart.")
        return redirect('view_cart')
    return redirect('shop')

def view_cart(request):
    cart = request.session.get('cart', {})
    cart_items = []
    total = 0

    for variant_id, item in cart.items():
        try:
            variant = ProductVariant.objects.select_related('product').get(id=variant_id)
            quantity = item['quantity']
            subtotal = quantity * variant.price
            total += subtotal
            cart_items.append({
                'variant': variant,
                'product': variant.product,
                'quantity': quantity,
                'total_price': subtotal
            })
        except ProductVariant.DoesNotExist:
            continue

    return render(request, 'shop/cart.html', {
        'cart_items': cart_items,
        'cart_total': total
    })

def remove_from_cart(request, variant_id):
    cart = request.session.get('cart', {})
    if str(variant_id) in cart:
        del cart[str(variant_id)]
        request.session['cart'] = cart
        messages.success(request, "Item removed from cart.")
    return redirect('view_cart')


@login_required
def checkout(request):
    cart = request.session.get('cart', {})
    cart_items = []
    total = 0

    for variant_id, item in cart.items():
        try:
            variant = ProductVariant.objects.get(id=variant_id)
            quantity = item.get('quantity', 1)
            subtotal = quantity * variant.price
            total += subtotal
            cart_items.append({
                'variant': variant,
                'quantity': quantity,
                'subtotal': subtotal
            })
        except ProductVariant.DoesNotExist:
            continue

    if request.method == 'POST':
        # process payment logic here
        pass

    return render(request, 'shop/checkout.html', {
        'cart_items': cart_items,
        'total': total
    })



@login_required
def payment_success(request):
    cart = request.session.get('cart', {})
    if not cart:
        return redirect('shop')

    total_price = 0
    order = Order.objects.create(
        user=request.user,
        total_price=0  # we'll update this below
    )

    for variant_id, item in cart.items():
        try:
            variant = ProductVariant.objects.get(id=variant_id)
            quantity = item['quantity']
            price = variant.price
            subtotal = quantity * price
            total_price += subtotal

            OrderItem.objects.create(
                order=order,
                dress_name=f"{variant.product.name} ({variant.color}, {variant.size})",
                quantity=quantity,
                price=price
            )
        except ProductVariant.DoesNotExist:
            continue

    order.total_price = total_price
    order.save()

    del request.session['cart']

    if request.user.email:
        send_mail(
            subject='Thank you for your order!',
            message=f"Hi {request.user.username},\n\nYour order #{order.id} has been received.",
            from_email=settings.EMAIL_HOST_USER,
            recipient_list=[request.user.email],
            fail_silently=True,
        )

    return render(request, 'shop/success.html', {'order': order})


def payment_cancel(request):
    return render(request, 'shop/cancel.html')

@csrf_exempt
def create_checkout_session(request):
    if request.method == 'POST':
        cart = request.session.get('cart', {})
        line_items = []

        for variant_id, item in cart.items():
            try:
                variant = ProductVariant.objects.get(id=variant_id)
                line_items.append({
                    'price_data': {
                        'currency': 'usd',
                        'unit_amount': int(variant.price * 100),
                        'product_data': {
                            'name': f"{variant.product.name} ({variant.color}, {variant.size})",
                        },
                    },
                    'quantity': item['quantity'],
                })
            except ProductVariant.DoesNotExist:
                continue

        session = stripe.checkout.Session.create(
            payment_method_types=['card'],
            line_items=line_items,
            mode='payment',
            success_url=request.build_absolute_uri(reverse('payment_success')),
            cancel_url=request.build_absolute_uri(reverse('payment_cancel')),
        )

        return JsonResponse({'id': session.id})

def register_view(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            auth_login(request, user)
            messages.success(request, "Account created and logged in.")
            return redirect('home')
    else:
        form = UserCreationForm()
    return render(request, 'shop/register.html', {'form': form})

def login_view(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            auth_login(request, user)
            messages.success(request, "Logged in successfully.")
            return redirect('home')
    else:
        form = AuthenticationForm()
    return render(request, 'shop/login.html', {'form': form})

def logout_view(request):
    auth_logout(request)
    messages.info(request, "Logged out successfully.")
    return redirect('home')

def view_orders(request):
    orders = Order.objects.filter(user=request.user).order_by('-created_at')
    return render(request, 'shop/my_orders.html', {'orders': orders})
