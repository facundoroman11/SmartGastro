import requests
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

    # --- Consumo de API de Clima  ---
    clima_data = None
    alerta_lluvia = False
    try:
        # Coordenadas de Buenos Aires
        url = "https://api.open-meteo.com/v1/forecast?latitude=-34.6037&longitude=-58.3816&daily=weathercode,temperature_2m_max,temperature_2m_min,precipitation_probability_max&timezone=auto"
        response = requests.get(url, timeout=5)
        
        if response.status_code == 200:
            data = response.json()
            prob_lluvia = data['daily']['precipitation_probability_max'][0]
            temp_max = data['daily']['temperature_2m_max'][0]
            temp_min = data['daily']['temperature_2m_min'][0]
            
            # Disparar alerta visual si la probabilidad de lluvia es superior al 50%
            if prob_lluvia is not None and prob_lluvia > 50:
                alerta_lluvia = True

            clima_data = {
                'temp_max': temp_max,
                'temp_min': temp_min,
                'prob_lluvia': prob_lluvia
            }
    except Exception as e:
        print(f"Error al obtener datos de la API del Clima: {e}")

    productos = Producto.objects.all()
    
    return render(request, 'core/inventario.html', {
        'productos': productos,
        'clima': clima_data,
        'alerta_lluvia': alerta_lluvia
    })

@login_required
def eliminar_producto(request, id):
    producto = get_object_or_404(Producto, id=id)
    producto.delete()
    return redirect('inventario')

def salir(request):
    logout(request)
    return redirect('login')

# Editar
@login_required
def editar_producto(request, id):
    producto = get_object_or_404(Producto, id=id)
    
    if request.method == 'POST':
        producto.nombre = request.POST.get('nombre')
        producto.cantidad = request.POST.get('cantidad')
        producto.unidad_medida = request.POST.get('unidad_medida')
        producto.precio_unitario = request.POST.get('precio_unitario')
        producto.stock_minimo = request.POST.get('stock_minimo')
        producto.save()
        return redirect('inventario')

    return render(request, 'core/editar_producto.html', {'producto': producto})