from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect
from core.models import Product
from django.contrib import messages
from ecommerce.settings import LOGIN_URL


def get_cart(request):
    cart = request.session.get("cart")
    if not cart:
        cart = request.session["cart"] = {}
    return cart


def add_to_cart(request, product_id):
    if request.user.is_authenticated:
        cart = get_cart(request)
        product = get_object_or_404(Product, id=product_id)
        product_id = str(product_id)
        if product_id not in cart:
            # Check stock first
            if product.stock <= 0:
                messages.error(
                    request, "No hay más productos en stock", extra_tags="danger"
                )
                return HttpResponseRedirect(request.META.get("HTTP_REFERER"))
            cart[product_id] = {
                "name": product.name,
                "image": product.get_main_image().image.url,
                "price": str(product.price),
                "amount": 1,
                "sum": str(product.price),
            }
        else:
            # Check stock first
            if int(cart[product_id]["amount"]) >= product.stock:
                messages.error(
                    request, "No hay más productos en stock", extra_tags="danger"
                )
                return HttpResponseRedirect(request.META.get("HTTP_REFERER"))
            cart[product_id]["amount"] += 1
            cart[product_id]["sum"] = "{:.2f}".format(
                float(cart[product_id]["sum"]) + float(cart[product_id]["price"])
            )
        messages.success(
            request, "Agregaste el producto al carrito", extra_tags="success"
        )
        request.session.modified = True
        return HttpResponseRedirect(request.META.get("HTTP_REFERER"))
    else:
        messages.error(
            request,
            "Por favor, iniciá sesión para agregar productos al carrito",
            extra_tags="warning",
        )
        return redirect(LOGIN_URL)


@login_required
def subtract_from_cart(request, product_id):
    cart = get_cart(request)
    product_id = str(product_id)
    if product_id in cart:
        if cart[product_id]["amount"] > 1:
            cart[product_id]["amount"] -= 1
            cart[product_id]["sum"] = "{:.2f}".format(
                float(cart[product_id]["sum"]) - float(cart[product_id]["price"])
            )
        else:
            del cart[product_id]
    messages.success(request, "Quitaste el producto del carrito", extra_tags="warning")
    request.session.modified = True
    return HttpResponseRedirect(request.META.get("HTTP_REFERER"))


@login_required
def remove_from_cart(request, product_id):
    cart = get_cart(request)
    product_id = str(product_id)
    if product_id in cart:
        del cart[product_id]
    messages.success(request, "Quitaste el producto del carrito", extra_tags="warning")
    request.session.modified = True
    return HttpResponseRedirect(request.META.get("HTTP_REFERER"))


@login_required
def clear_cart(request):
    request.session["cart"] = {}
    messages.success(request, "Tu carrito ahora está vacío", extra_tags="warning")
    request.session.modified = True
    return HttpResponseRedirect(request.META.get("HTTP_REFERER"))
