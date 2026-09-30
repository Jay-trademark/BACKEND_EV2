from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from .models import carrito_productos, categorias, marcas, productos, usuarios


class CartProductEndpointsTests(APITestCase):
	def setUp(self):
		user_model = get_user_model()
		self.auth_user = user_model.objects.create_user(
			username="cart-customer",
			password="test-password",
		)
		self.profile = usuarios.objects.create(
			firstname="Test",
			lastname="Customer",
			email="customer@example.com",
			user=self.auth_user,
		)
		category = categorias.objects.create(nombre="Components")
		brand = marcas.objects.create(nombre="Example")
		self.product = productos.objects.create(
			nombre="Keyboard",
			precio_un="25.00",
			codigo_sku="KEYBOARD-001",
			descripcion="Test product",
			stock=5,
			categoria=category,
			marca=brand,
		)

	def test_add_update_list_and_remove_product(self):
		list_url = reverse("cart-products", args=[self.profile.id])
		add_response = self.client.post(
			list_url,
			{"producto_id": self.product.id, "cantidad": 2},
			format="json",
		)

		self.assertEqual(add_response.status_code, status.HTTP_201_CREATED)
		self.assertEqual(add_response.data["cantidad"], 2)

		add_again_response = self.client.post(
			list_url,
			{"producto_id": self.product.id, "cantidad": 1},
			format="json",
		)
		self.assertEqual(add_again_response.status_code, status.HTTP_200_OK)
		self.assertEqual(add_again_response.data["cantidad"], 3)

		detail_url = reverse("cart-product-detail", args=[self.profile.id, self.product.id])
		update_response = self.client.patch(
			detail_url,
			{"cantidad": 4},
			format="json",
		)
		self.assertEqual(update_response.status_code, status.HTTP_200_OK)
		self.assertEqual(update_response.data["cantidad"], 4)

		list_response = self.client.get(list_url)
		self.assertEqual(list_response.status_code, status.HTTP_200_OK)
		self.assertEqual(list_response.data[0]["cantidad"], 4)

		delete_response = self.client.delete(detail_url)
		self.assertEqual(delete_response.status_code, status.HTTP_204_NO_CONTENT)
		self.assertFalse(carrito_productos.objects.exists())

	def test_reject_quantity_above_stock(self):
		response = self.client.post(
			reverse("cart-products", args=[self.profile.id]),
			{"producto_id": self.product.id, "cantidad": 6},
			format="json",
		)

		self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
		self.assertFalse(carrito_productos.objects.exists())
