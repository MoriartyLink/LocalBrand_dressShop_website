from django.shortcuts import render, redirect
from .models import Dress, Order, OrderItem
from django.views.decorators.csrf import csrf_exempt
import stripe
from django.conf import settings
from django.http import JsonResponse
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.contrib import messages
from django.core.mail import send_mail
import stripe
from django.urls import reverse
from django.conf import settings
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth import login as auth_login, authenticate, logout as auth_logout

stripe.api_key = settings.STRIPE_SECRET_KEY

def home(request):
    featured_dresses = Dress.objects.all()[:6]  # Show top 6 dresses
    return render(request, 'shop/home.html', {'featured_dresses': featured_dresses})

def shop(request):
    dresses = Dress.objects.all()
    return render(request, 'shop/shop.html', {'dresses': dresses})

def add_to_cart(request, dress_id):
    cart = request.session.get('cart',{})

    if str(dress_id) in cart:
        cart[str(dress_id)] += 1
    else:
        cart[str(dress_id)] = 1

    request .session['cart'] = cart
    return redirect('shop')

def view_cart(request):
    cart = request.session.get('cart', {})
    dresses = Dress.objects.filter(id__in=cart.keys())
    cart_items = []
    total = 0

    for dress in dresses:
        quantity = cart[str(dress.id)]
        item_total = dress.price * quantity
        total += item_total
        cart_items.append({
            'dress': dress,
            'quantity': quantity,
            'total': item_total
        })

    return render(request, 'shop/cart.html', {
        'cart_items': cart_items,
        'total': total
    })


def remove_from_cart(request, dress_id):
    cart = request.session.get('cart',{})

    if str(dress_id) in cart:
        del cart[str(dress_id)]
        request.session['cart'] = cart

    return redirect('view_cart')

def checkout(request):
    cart = request.session.get('cart', {})
    dresses = Dress.objects.filter(id__in=cart.keys())
    total = 0
    total_items = 0

    for dress in dresses:
        qty = cart.get(str(dress.id), 0)
        total += dress.price * qty
        total_items += qty

    if request.method == 'POST':
        success_url = request.build_absolute_uri(reverse('payment_success'))
        cancel_url = request.build_absolute_uri(reverse('payment_cancel'))

        # Stripe session
        session = stripe.checkout.Session.create(
            payment_method_types=['card'],
            line_items=[
                {
                    'price_data': {
                        'currency': 'usd',
                        'unit_amount': int(dress.price * 100),
                        'product_data': {
                            'name': dress.name,
                        },
                    },
                    'quantity': cart.get(str(dress.id), 0),
                } for dress in dresses
            ],
            mode='payment',
            success_url=success_url,
            cancel_url=cancel_url,
        )
        return redirect(session.url, code=303)

    return render(request, 'shop/checkout.html', {
        'total': total,
        'total_items': total_items,
    })

@csrf_exempt
def create_checkout_session(request):
    cart = request.session.get('cart', {})
    dresses = Dress.objects.filter(id__in=cart.keys())

    line_items = []

    for dress in dresses:
        quantity = cart[str(dress.id)]
        line_items.append({
            'price_data': {
                'currency': 'usd',
                'unit_amount': int(dress.price * 100),  # Stripe expects cents
                'product_data': {
                    'name': dress.name,
                },
            },
            'quantity': quantity,
        })

    stripe.api_key = settings.STRIPE_SECRET_KEY

    session = stripe.checkout.Session.create(
        payment_method_types=['card'],
        line_items=line_items,
        mode='payment',
        success_url='http://127.0.0.1:8000/success/',
        cancel_url='http://127.0.0.1:8000/cancel/',
    )

    return JsonResponse({'id': session.id})

def payment_success(request):
    cart = request.session.get('cart', {})
    if not cart:
        return redirect('shop')  # prevent empty orders

    dresses = Dress.objects.filter(id__in=cart.keys())

    total_price = 0
    for dress in dresses:
        quantity = cart[str(dress.id)]
        total_price += dress.price * quantity

    # Create the Order
    order = Order.objects.create(
        user=request.user if request.user.is_authenticated else None,
        total_price=total_price
    )
    items_summary = ""
    for dress in dresses:
        quantity = cart[str(dress.id)]
        OrderItem.objects.create(
            order=order,
            dress_name=dress.name,
            quantity=quantity,
            price=dress.price
        )
        items_summary += f"{quantity} × {dress.name} - ${dress.price}\n"

    # Clear the cart
    del request.session['cart']
    if request.user.is_authenticated and request.user.email:
        send_mail(
            subject='Your Order Confirmation - Local Brand Shop',
            message=f"Hi {request.user.username},\n\n"
                    f"Thank you for your order #{order.id}!\n\n"
                    f"Order Summary:\n{items_summary}\n"
                    f"Total: ${order.total_price}\n\n"
                    f"We'll notify you once it's shipped.",
            from_email=settings.EMAIL_HOST_USER,
            recipient_list=[request.user.email],
            fail_silently=False,
        )
    return render(request, 'shop/success.html', {'order': order})


def payment_cancel(request):
    return render(request, 'shop/cancel.html')


def register_view(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            auth_login(request, user)
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
            return redirect('home')
    else:
        form = AuthenticationForm()
    return render(request, 'shop/login.html', {'form': form})

def logout_view(request):
    logout(request)
    return redirect('shop')

@login_required
def view_orders(request):
    orders = Order.objects.filter(user=request.user).order_by('-created_at')
    return render(request, 'shop/my_orders.html', {'orders': orders})