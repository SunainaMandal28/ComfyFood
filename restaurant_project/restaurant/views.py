
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from django.contrib import messages
from .models import MenuItem, Reservation, Order, OrderItem
from django.db import transaction
from django.views.decorators.http import require_POST
from django.utils import timezone
from django.contrib import messages


# Home & Menu
def home(request):
    items = MenuItem.objects.filter(is_available=True)[:6]
    return render(request, 'index.html', {'items': items})

def menu_page(request):
    items = MenuItem.objects.filter(is_available=True)
    return render(request, 'menu.html', {'items': items})

# Contact 
def contact_page(request):
    if request.method == "POST":
        pass
    return render(request, "contact.html")

# Reservations
'''def reservation_create(request):
    if request.method == "POST":
        name = request.POST.get('name')
        email = request.POST.get('email')
        phone = request.POST.get('phone')
        date = request.POST.get('date')  # 'YYYY-MM-DD'
        time = request.POST.get('time')  # 'HH:MM'
        party_size = int(request.POST.get('party_size', 1))
        notes = request.POST.get('notes','')
        Reservation.objects.create(
            full_name=name, email=email, phone=phone,
            date=date, time=time, party_size=party_size, notes=notes
        )
        messages.success(request, "Reservation request received. We'll confirm it soon.")
        return redirect('reservation')
    return render(request, 'reservation.html')'''

'''def reservation_create(request):
    if request.method == "POST":
        name = request.POST.get('name')
        email = request.POST.get('email')
        phone = request.POST.get('phone')
        date = request.POST.get('date')
        time = request.POST.get('time')
        party_size = request.POST.get('party_size')
        notes = request.POST.get('notes', '')

        Reservation.objects.create(
            full_name=name,
            email=email,
            phone=phone,
            date=date,
            time=time,
            party_size=party_size,
            notes=notes,
            confirmed=False,
        )

        messages.success(request, "Your reservation request has been submitted. We will confirm soon.")

        return redirect("reservation")

    # show existing confirmed reservations for logged user? (optional)
    return render(request, "reservation.html")
'''


def reservation_create(request):
    if request.method == "POST":
        name = request.POST.get("name")
        email = request.POST.get("email")
        phone = request.POST.get("phone")
        date = request.POST.get("date")
        time = request.POST.get("time")
        party_size = request.POST.get("party_size", 1)
        notes = request.POST.get("notes", "")

        Reservation.objects.create(
            name=name,
            email=email,
            phone=phone,
            date=date,
            time=time,
            party_size=party_size,
            notes=notes
        )

        messages.success(request, "Your reservation request has been submitted. We'll confirm it soon.")
        return redirect("reservation")
    reservations = Reservation.objects.order_by('-created_at')[:5]
    return render(request, "reservation.html", {"reservations": reservations})


'''def _get_cart(request):
    return request.session.get('cart', {})

def _save_cart(request, cart):
    request.session['cart'] = cart
    request.session.modified = True'''
def _get_cart(request):
    return request.session.get('cart', {})  

def _save_cart(request, cart):
    request.session['cart'] = cart
    request.session.modified = True 


@require_POST
def cart_add(request, item_id):
    cart = request.session.get('cart', {})
    qty = int(request.POST.get('quantity', 1))

    if str(item_id) in cart:
        cart[str(item_id)] += qty
    else:
        cart[str(item_id)] = qty

    request.session['cart'] = cart
    request.session.modified = True
    messages.success(request, "Added to cart.")
    return redirect('cart')

def cart_view(request):
    cart = request.session.get('cart', {})
    items = []
    total = 0

    for item_id, qty in cart.items():
        item = get_object_or_404(MenuItem, pk=int(item_id))
        line_total = item.price * qty
        items.append({'item': item, 'quantity': qty, 'line_total': line_total})
        total += line_total

    return render(request, 'cart.html', {'cart_items': items, 'total': total})

@require_POST
def cart_remove(request, item_id):
    cart = request.session.get('cart', {})
    cart.pop(str(item_id), None)
    request.session['cart'] = cart
    request.session.modified = True
    messages.info(request, "Item removed from cart.")
    return redirect('cart')

# Update item quantity
@require_POST
def cart_update(request, item_id):
    cart = request.session.get('cart', {})
    qty = int(request.POST.get('quantity', 1))

    if qty <= 0:
        cart.pop(str(item_id), None)
    else:
        cart[str(item_id)] = qty

    request.session['cart'] = cart
    request.session.modified = True
    messages.success(request, "Cart updated.")
    return redirect('cart')

@transaction.atomic
def checkout(request):
    cart = _get_cart(request)
    if not cart:
        messages.info(request, "Your cart is empty.")
        return redirect('menu')

    if request.method == "POST":
        name = request.POST.get('name')
        email = request.POST.get('email')
        phone = request.POST.get('phone')
        address = request.POST.get('address','')
        order = Order.objects.create(
            customer_name=name, customer_email=email,
            customer_phone=phone, address=address
        )
        total = 0
        for item_id, qty in cart.items():
            menu_item = MenuItem.objects.get(pk=int(item_id))
            price = menu_item.price
            OrderItem.objects.create(order=order, menu_item=menu_item, quantity=qty, price=price)
            total += price * qty
        order.total = total
        order.save()
        # clear cart
        request.session['cart'] = {}
        messages.success(request, f"Order placed! Your order number is {order.id}")
        return redirect('order_success', order_id=order.id)

    items = []
    total = 0
    for item_id, qty in cart.items():
        menu_item = MenuItem.objects.get(pk=int(item_id))
        items.append({'item': menu_item, 'quantity': qty, 'line_total': menu_item.price * qty})
        total += menu_item.price * qty
    return render(request, 'checkout.html', {'cart_items': items, 'total': total})

def order_success(request, order_id):
    order = get_object_or_404(Order, pk=order_id)
    return render(request, 'order_success.html', {'order': order})

def about ( request):
     return render(request, 'about.html')