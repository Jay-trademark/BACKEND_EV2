from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.exceptions import NotFound, ValidationError
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import carrito, carrito_productos, productos, usuarios
from .serializers import AddCartProductSerializer, UpdateCartQuantitySerializer


def _get_profile(usuario_id):
    return get_object_or_404(usuarios, pk=usuario_id)


def _get_cart_item_data(item):
    product = item.producto
    return {
        "producto_id": product.id,
        "nombre": product.nombre,
        "codigo_sku": product.codigo_sku,
        "precio_un": str(product.precio_un),
        "cantidad": item.cantidad,
        "subtotal": str(product.precio_un * item.cantidad),
    }


class CartProductListCreateView(APIView):
    permission_classes = [AllowAny]

    def get(self, request, usuario_id):
        profile = _get_profile(usuario_id)
        cart = profile.carrito.order_by("id").first()
        if cart is None:
            return Response([])

        items = carrito_productos.objects.filter(carrito=cart).select_related("producto")
        return Response([_get_cart_item_data(item) for item in items])

    def post(self, request, usuario_id):
        profile = _get_profile(usuario_id)
        serializer = AddCartProductSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        product = get_object_or_404(productos, pk=serializer.validated_data["producto_id"])
        quantity = serializer.validated_data["cantidad"]
        if quantity > product.stock:
            raise ValidationError({"cantidad": "La cantidad solicitada supera el stock disponible."})

        cart = profile.carrito.order_by("id").first()
        if cart is None:
            cart = carrito.objects.create(usuario=profile)
        item, created = carrito_productos.objects.get_or_create(
            carrito=cart,
            producto=product,
            defaults={"cantidad": quantity},
        )
        if not created:
            new_quantity = item.cantidad + quantity
            if new_quantity > product.stock:
                raise ValidationError({"cantidad": "La cantidad solicitada supera el stock disponible."})
            item.cantidad = new_quantity
            item.save(update_fields=["cantidad"])

        response_status = status.HTTP_201_CREATED if created else status.HTTP_200_OK
        return Response(_get_cart_item_data(item), status=response_status)


class CartProductDetailView(APIView):
    permission_classes = [AllowAny]

    def _get_item(self, usuario_id, product_id):
        profile = _get_profile(usuario_id)
        cart = profile.carrito.order_by("id").first()
        if cart is None:
            raise NotFound("El carrito no existe.")
        return get_object_or_404(
            carrito_productos.objects.select_related("producto"),
            carrito=cart,
            producto_id=product_id,
        )

    def patch(self, request, usuario_id, product_id):
        item = self._get_item(usuario_id, product_id)
        serializer = UpdateCartQuantitySerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        quantity = serializer.validated_data["cantidad"]
        if quantity > item.producto.stock:
            raise ValidationError({"cantidad": "La cantidad solicitada supera el stock disponible."})

        item.cantidad = quantity
        item.save(update_fields=["cantidad"])
        return Response(_get_cart_item_data(item))

    def delete(self, request, usuario_id, product_id):
        item = self._get_item(usuario_id, product_id)
        item.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
