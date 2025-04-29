from django.shortcuts import render, redirect
from .models import Dress

def home(request):
    return render(request, 'shop/home.html')

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
    cart = request.session.get('cart',{})
    dresses = Dress.objects.filter(id__in=cart.key())

    cart_items = []
    total_price = 0

    for dress in dresses :
        quantity = cart[str(dress.id)]
        total = dress.price * quantity
        total_price += total
        cart_items.append({
            'dress':dress,
            'quantity':quantity,
            'total':total,
        })

        context = {
            'cart_items':cart_items,
            'total_price':total_price,
        }
        return render(request, 'shop/cart.html',context)

def remove_from_cart(request, dress_id):
    cart = request.session.get('cart',{})

    if str(dress_id) in cart:
        del cart[str(dress_id)]
        request.session['cart'] = cart

    return redirect('view_cart')

def checkout(request):
    cart = request.session.get('cart',{})
    dresses = Dress.objects.filter(id__in=cart.keys())

    cart_items = []
    total_price = 0

    for dress in dresses :
        quantity = cart [str(dress.id)]
        total = dress.price * quantity
        total_price += total
        cart_items.append({
            'dress': dress,
            'quantity': quantity,
            'total': total,
        }
        )

    context = {
        'cart_items':cart_items,
        'total_price':total_price,
    }
    return render(request,'shop/checkout.html',context)

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
