from django.urls import path
from . import views

app_name = 'inventario'

urlpatterns = [
    # Auth
    path('', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),

    # Dashboard
    path('dashboard/', views.dashboard, name='dashboard'),

    # Categorías
    path('categorias/', views.categorias_lista, name='categorias'),
    path('categorias/crear/', views.categoria_crear, name='categoria_crear'),
    path('categorias/editar/<int:pk>/', views.categoria_editar, name='categoria_editar'),
    path('categorias/eliminar/<int:pk>/', views.categoria_eliminar, name='categoria_eliminar'),

    # Productos
    path('productos/', views.productos_lista, name='productos'),
    path('productos/crear/', views.producto_crear, name='producto_crear'),
    path('productos/editar/<int:pk>/', views.producto_editar, name='producto_editar'),
    path('productos/eliminar/<int:pk>/', views.producto_eliminar, name='producto_eliminar'),

    # Inventario
    path('inventario/', views.inventario_lista, name='inventario'),
    path('inventario/editar/<int:pk>/', views.inventario_editar, name='inventario_editar'),

    # Movimientos
    path('movimientos/', views.movimientos_lista, name='movimientos'),
    path('movimientos/crear/', views.movimiento_crear, name='movimiento_crear'),

    # Acciones
    path('acciones/', views.acciones_lista, name='acciones'),
]