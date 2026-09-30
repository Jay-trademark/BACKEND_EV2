from rest_framework import serializers


class AddCartProductSerializer(serializers.Serializer):
    producto_id = serializers.IntegerField(min_value=1)
    cantidad = serializers.IntegerField(min_value=1, default=1)


class UpdateCartQuantitySerializer(serializers.Serializer):
    cantidad = serializers.IntegerField(min_value=1)