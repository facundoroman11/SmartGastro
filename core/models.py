from django.db import models

class Producto(models.Model):
    nombre = models.CharField(max_length=100)
    cantidad = models.DecimalField(max_digits=10, decimal_places=2, default=0.0)
    unidad_medida = models.CharField(max_length=20, default='unidad')  # Ej: kg, litros, unidades
    precio_unitario = models.DecimalField(max_digits=10, decimal_places=2, default=0.0)
    stock_minimo = models.DecimalField(max_digits=10, decimal_places=2, default=5.0)

    def __str__(self):
        return f"{self.nombre} ({self.cantidad} {self.unidad_medida})"