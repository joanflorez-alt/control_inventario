from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib import messages
from django.db.models import Q, F
from .models import Categoria, Producto, Inventario, MovimientoInventario, RegistroAccion


# ─────────────────────────────────────────
# AUTENTICACIÓN
# ─────────────────────────────────────────

def login_view(request):
    if request.user.is_authenticated:
        return redirect('inventario:dashboard')
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            RegistroAccion.objects.create(
                usuario=user,
                accion='Login',
                descripcion=f'El usuario {user.username} inició sesión.'
            )
            return redirect('inventario:dashboard')
        else:
            messages.error(request, 'Usuario o contraseña incorrectos.')
    return render(request, 'inventario/login.html')


@login_required(login_url='inventario:login')
def logout_view(request):
    RegistroAccion.objects.create(
        usuario=request.user,
        accion='Logout',
        descripcion=f'El usuario {request.user.username} cerró sesión.'
    )
    logout(request)
    return redirect('inventario:login')


# ─────────────────────────────────────────
# DASHBOARD
# ─────────────────────────────────────────

@login_required(login_url='inventario:login')
def dashboard(request):
    total_productos = Producto.objects.count()
    total_categorias = Categoria.objects.count()
    alertas = Inventario.objects.filter(
        cantidad_actual__lte=F('stock_minimo')
    ).select_related('producto')
    movimientos_recientes = MovimientoInventario.objects.select_related(
        'producto', 'usuario'
    )[:5]
    context = {
        'total_productos': total_productos,
        'total_categorias': total_categorias,
        'alertas': alertas,
        'movimientos_recientes': movimientos_recientes,
    }
    return render(request, 'inventario/dashboard.html', context)


# ─────────────────────────────────────────
# CATEGORÍAS
# ─────────────────────────────────────────

@login_required(login_url='inventario:login')
def categorias_lista(request):
    categorias = Categoria.objects.all()
    return render(request, 'inventario/categorias.html', {'categorias': categorias})


@login_required(login_url='inventario:login')
def categoria_crear(request):
    if request.method == 'POST':
        nombre = request.POST.get('nombre')
        descripcion = request.POST.get('descripcion', '')
        if nombre:
            Categoria.objects.create(nombre=nombre, descripcion=descripcion)
            RegistroAccion.objects.create(
                usuario=request.user,
                accion='Crear categoría',
                descripcion=f'Se creó la categoría: {nombre}'
            )
            messages.success(request, 'Categoría creada correctamente.')
            return redirect('inventario:categorias')
        else:
            messages.error(request, 'El nombre es obligatorio.')
    return render(request, 'inventario/categoria_form.html')


@login_required(login_url='inventario:login')
def categoria_editar(request, pk):
    categoria = get_object_or_404(Categoria, pk=pk)
    if request.method == 'POST':
        nombre = request.POST.get('nombre')
        descripcion = request.POST.get('descripcion', '')
        if nombre:
            categoria.nombre = nombre
            categoria.descripcion = descripcion
            categoria.save()
            RegistroAccion.objects.create(
                usuario=request.user,
                accion='Editar categoría',
                descripcion=f'Se editó la categoría: {nombre}'
            )
            messages.success(request, 'Categoría actualizada.')
            return redirect('inventario:categorias')
    return render(request, 'inventario/categoria_form.html', {'categoria': categoria})


@login_required(login_url='inventario:login')
def categoria_eliminar(request, pk):
    categoria = get_object_or_404(Categoria, pk=pk)
    if request.method == 'POST':
        nombre = categoria.nombre
        categoria.delete()
        RegistroAccion.objects.create(
            usuario=request.user,
            accion='Eliminar categoría',
            descripcion=f'Se eliminó la categoría: {nombre}'
        )
        messages.success(request, 'Categoría eliminada.')
        return redirect('inventario:categorias')
    return render(request, 'inventario/confirmar_eliminar.html', {'objeto': categoria, 'tipo': 'categoría'})


# ─────────────────────────────────────────
# PRODUCTOS
# ─────────────────────────────────────────

@login_required(login_url='inventario:login')
def productos_lista(request):
    query = request.GET.get('q', '')
    categoria_id = request.GET.get('categoria', '')
    productos = Producto.objects.select_related('categoria').all()
    if query:
        productos = productos.filter(
            Q(nombre__icontains=query) | Q(codigo_barras__icontains=query)
        )
    if categoria_id:
        productos = productos.filter(categoria__id=categoria_id)
    categorias = Categoria.objects.all()
    context = {
        'productos': productos,
        'categorias': categorias,
        'query': query,
        'categoria_id': categoria_id,
    }
    return render(request, 'inventario/productos.html', context)


@login_required(login_url='inventario:login')
def producto_crear(request):
    categorias = Categoria.objects.all()
    if request.method == 'POST':
        nombre = request.POST.get('nombre')
        descripcion = request.POST.get('descripcion', '')
        codigo_barras = request.POST.get('codigo_barras', '') or None
        precio = request.POST.get('precio')
        categoria_id = request.POST.get('categoria') or None
        imagen = request.FILES.get('imagen')
        if nombre and precio:
            producto = Producto.objects.create(
                nombre=nombre,
                descripcion=descripcion,
                codigo_barras=codigo_barras,
                precio=precio,
                categoria_id=categoria_id,
                imagen=imagen,
            )
            Inventario.objects.create(producto=producto)
            RegistroAccion.objects.create(
                usuario=request.user,
                accion='Crear producto',
                descripcion=f'Se creó el producto: {nombre}'
            )
            messages.success(request, 'Producto creado correctamente.')
            return redirect('inventario:productos')
        else:
            messages.error(request, 'Nombre y precio son obligatorios.')
    return render(request, 'inventario/producto_form.html', {'categorias': categorias})


@login_required(login_url='inventario:login')
def producto_editar(request, pk):
    producto = get_object_or_404(Producto, pk=pk)
    categorias = Categoria.objects.all()
    if request.method == 'POST':
        producto.nombre = request.POST.get('nombre')
        producto.descripcion = request.POST.get('descripcion', '')
        producto.codigo_barras = request.POST.get('codigo_barras', '') or None
        producto.precio = request.POST.get('precio')
        producto.categoria_id = request.POST.get('categoria') or None
        if request.FILES.get('imagen'):
            producto.imagen = request.FILES.get('imagen')
        producto.save()
        RegistroAccion.objects.create(
            usuario=request.user,
            accion='Editar producto',
            descripcion=f'Se editó el producto: {producto.nombre}'
        )
        messages.success(request, 'Producto actualizado.')
        return redirect('inventario:productos')
    return render(request, 'inventario/producto_form.html', {
        'producto': producto,
        'categorias': categorias
    })


@login_required(login_url='inventario:login')
def producto_eliminar(request, pk):
    producto = get_object_or_404(Producto, pk=pk)
    if request.method == 'POST':
        nombre = producto.nombre
        producto.delete()
        RegistroAccion.objects.create(
            usuario=request.user,
            accion='Eliminar producto',
            descripcion=f'Se eliminó el producto: {nombre}'
        )
        messages.success(request, 'Producto eliminado.')
        return redirect('inventario:productos')
    return render(request, 'inventario/confirmar_eliminar.html', {'objeto': producto, 'tipo': 'producto'})


# ─────────────────────────────────────────
# INVENTARIO
# ─────────────────────────────────────────

@login_required(login_url='inventario:login')
def inventario_lista(request):
    inventarios = Inventario.objects.select_related('producto__categoria').all()
    return render(request, 'inventario/inventario.html', {'inventarios': inventarios})


@login_required(login_url='inventario:login')
def inventario_editar(request, pk):
    inv = get_object_or_404(Inventario, pk=pk)
    if request.method == 'POST':
        cantidad = request.POST.get('cantidad_actual')
        stock_minimo = request.POST.get('stock_minimo')
        if cantidad is not None and stock_minimo is not None:
            inv.cantidad_actual = int(cantidad)
            inv.stock_minimo = int(stock_minimo)
            inv.save()
            RegistroAccion.objects.create(
                usuario=request.user,
                accion='Editar inventario',
                descripcion=f'Se actualizó el inventario de: {inv.producto.nombre}'
            )
            messages.success(request, 'Inventario actualizado.')
            return redirect('inventario:inventario')
    return render(request, 'inventario/inventario_form.html', {'inv': inv})


# ─────────────────────────────────────────
# MOVIMIENTOS
# ─────────────────────────────────────────

@login_required(login_url='inventario:login')
def movimientos_lista(request):
    producto_id = request.GET.get('producto', '')
    movimientos = MovimientoInventario.objects.select_related('producto', 'usuario').all()
    if producto_id:
        movimientos = movimientos.filter(producto__id=producto_id)
    productos = Producto.objects.all()
    context = {
        'movimientos': movimientos,
        'productos': productos,
        'producto_id': producto_id,
    }
    return render(request, 'inventario/movimientos.html', context)


@login_required(login_url='inventario:login')
def movimiento_crear(request):
    productos = Producto.objects.all()
    if request.method == 'POST':
        producto_id = request.POST.get('producto')
        tipo = request.POST.get('tipo')
        cantidad = request.POST.get('cantidad')
        motivo = request.POST.get('motivo', '')
        if producto_id and tipo and cantidad:
            cantidad = int(cantidad)
            producto = get_object_or_404(Producto, pk=producto_id)
            # Validar que no haya salida con stock insuficiente
            if tipo == 'salida':
                inv, _ = Inventario.objects.get_or_create(producto=producto)
                if cantidad > inv.cantidad_actual:
                    messages.error(request, f'Stock insuficiente. Disponible: {inv.cantidad_actual}')
                    return render(request, 'inventario/movimiento_form.html', {'productos': productos})
            MovimientoInventario.objects.create(
                producto=producto,
                usuario=request.user,
                tipo=tipo,
                cantidad=cantidad,
                motivo=motivo,
            )
            RegistroAccion.objects.create(
                usuario=request.user,
                accion=f'Movimiento {tipo}',
                descripcion=f'{tipo.capitalize()} de {cantidad} unidades de {producto.nombre}. Motivo: {motivo}'
            )
            messages.success(request, f'Movimiento de {tipo} registrado correctamente.')
            return redirect('inventario:movimientos')
        else:
            messages.error(request, 'Todos los campos son obligatorios.')
    return render(request, 'inventario/movimiento_form.html', {'productos': productos})


# ─────────────────────────────────────────
# REGISTRO DE ACCIONES
# ─────────────────────────────────────────

@login_required(login_url='inventario:login')
def acciones_lista(request):
    acciones = RegistroAccion.objects.select_related('usuario').all()
    return render(request, 'inventario/acciones.html', {'acciones': acciones})