from django.db import models
from django.conf import settings

# Create your models here.

#   Usuarios - general
class usuarios(models.Model):
    class Role(models.TextChoices):
        ADMIN = "admin", "Administrador"
        STAFF = "admin_ti", "Administradores de TI" # gestionan categorias y productos
        USER = "clientes", "Usuario"
        
    firstname = models.CharField(max_length=100)
    lastname = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    is_active = models.BooleanField(default=True)
    role = models.CharField(max_length=15, choices=Role.choices, default=Role.USER)
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="perfil",  # request.user.perfil.role
    )

class productos(models.Model):
    nombre = models.CharField(max_length=100)
    precio_un = models.DecimalField(max_digits=10, decimal_places=2)
    codigo_sku = models.CharField(max_length=32, unique=True)
    descripcion = models.TextField()
    stock = models.PositiveIntegerField()

    categoria = models.ForeignKey('categorias', on_delete=models.CASCADE, related_name='productos')
    marca = models.ForeignKey('marcas', on_delete=models.CASCADE, related_name='productos')

class marcas(models.Model):
    nombre = models.CharField(max_length=100) # Intel - AMD - NVIDIA - Kingston

class categorias(models.Model):
    nombre = models.CharField(max_length=100) # Procesadores - Tarjetas de Video - RAM

class carrito(models.Model):
    usuario = models.ForeignKey(usuarios, on_delete=models.CASCADE, related_name='carrito')
    productos = models.ManyToManyField(productos, through='carrito_productos', related_name='carrito')

class carrito_productos(models.Model):
    carrito = models.ForeignKey(carrito, on_delete=models.CASCADE, related_name='items')
    producto = models.ForeignKey(productos, on_delete=models.CASCADE, related_name='items_carrito')
    cantidad = models.PositiveIntegerField(default=1)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["carrito", "producto"],
                name="producto_unico_por_carrito",
            )
        ]

