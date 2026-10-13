from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth import logout
from .models import Producto

@login_required
def inventario(request):
    if request.method == 'POST':
        nombre = request.POST.get('nombre')
        cantidad = request.POST.get('cantidad')
        unidad_medida = request.POST.get('unidad_medida')
        precio_unitario = request.POST.get('precio_unitario')
        stock_minimo = request.POST.get('stock_minimo')

        Producto.objects.create(
            nombre=nombre,
            cantidad=cantidad,
            unidad_medida=unidad_medida,
            precio_unitario=precio_unitario,
            stock_minimo=stock_minimo
        )
        return redirect('inventario')

    productos = Producto.objects.all()
    return render(request, 'core/inventario.html', {'productos': productos})

@login_required
def eliminar_producto(request, id):
    producto = get_object_or_404(Producto, id=id)
    producto.delete()
    return redirect('inventario')

def salir(request):
    logout(request)
    return redirect('login')