from django.urls import path

from .views import CartProductDetailView, CartProductListCreateView

urlpatterns = [
    path(
        "usuarios/<int:usuario_id>/carrito/productos/",
        CartProductListCreateView.as_view(),
        name="cart-products",
    ),
    path(
        "usuarios/<int:usuario_id>/carrito/productos/<int:product_id>/",
        CartProductDetailView.as_view(),
        name="cart-product-detail",
    ),
]