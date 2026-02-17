from .models import Cart

def cart_items(request):
    """Контекстный процессор для количества товаров в корзине"""
    cart_items = 0
    if request.user.is_authenticated:
        try:
            cart = Cart.objects.get(user=request.user)
            cart_items = cart.get_total_items()
        except Cart.DoesNotExist:
            pass
    return {'cart_items': cart_items}