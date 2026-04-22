from django.contrib import admin
from .models import Categoria, Producto, Inventario, MovimientoInventario, RegistroAccion


@admin.register(Categoria)
class CategoriaAdmin(admin.ModelAdmin):
    list_display = ['nombre', 'descripcion']
    search_fields = ['nombre']


@admin.register(Producto)
class ProductoAdmin(admin.ModelAdmin):
    list_display = ['nombre', 'categoria', 'precio', 'codigo_barras']
    search_fields = ['nombre', 'codigo_barras']
    list_filter = ['categoria']


@admin.register(Inventario)
class InventarioAdmin(admin.ModelAdmin):
    list_display = ['producto', 'cantidad_actual', 'stock_minimo', 'tiene_stock_bajo']
    list_filter = ['producto__categoria']


@admin.register(MovimientoInventario)
class MovimientoInventarioAdmin(admin.ModelAdmin):
    list_display = ['producto', 'tipo', 'cantidad', 'usuario', 'fecha', 'motivo']
    list_filter = ['tipo', 'fecha']
    search_fields = ['producto__nombre', 'motivo']


@admin.register(RegistroAccion)
class RegistroAccionAdmin(admin.ModelAdmin):
    list_display = ['accion', 'usuario', 'fecha_hora']
    list_filter = ['accion']