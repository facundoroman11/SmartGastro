import requests
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth import logout
from django.db.models import Sum
from django.utils import timezone
from .models import Producto, Venta, DetalleVenta
from django.contrib import messages


@login_required
def inventario(request):
    if request.method == "POST":
        nombre = request.POST.get("nombre")
        cantidad = request.POST.get("cantidad")
        unidad_medida = request.POST.get("unidad_medida")
        precio_unitario = request.POST.get("precio_unitario")
        stock_minimo = request.POST.get("stock_minimo")

        Producto.objects.create(
            nombre=nombre,
            cantidad=cantidad,
            unidad_medida=unidad_medida,
            precio_unitario=precio_unitario,
            stock_minimo=stock_minimo,
        )
        return redirect("inventario")

    # --- Consumo de API de Clima  ---
    clima_data = None
    alerta_lluvia = False
    try:
        # Coordenadas de Buenos Aires
        url = "https://api.open-meteo.com/v1/forecast?latitude=-34.6037&longitude=-58.3816&daily=weathercode,temperature_2m_max,temperature_2m_min,precipitation_probability_max&timezone=auto"
        response = requests.get(url, timeout=5)

        if response.status_code == 200:
            data = response.json()
            prob_lluvia = data["daily"]["precipitation_probability_max"][0]
            temp_max = data["daily"]["temperature_2m_max"][0]
            temp_min = data["daily"]["temperature_2m_min"][0]

            # Disparar alerta visual si la probabilidad de lluvia es superior al 50%
            if prob_lluvia is not None and prob_lluvia > 50:
                alerta_lluvia = True

            clima_data = {
                "temp_max": temp_max,
                "temp_min": temp_min,
                "prob_lluvia": prob_lluvia,
            }
    except Exception as e:
        print(f"Error al obtener datos de la API del Clima: {e}")

    productos = Producto.objects.all()

    return render(
        request,
        "core/inventario.html",
        {"productos": productos, "clima": clima_data, "alerta_lluvia": alerta_lluvia},
    )


@login_required
def ventas(request):
    if request.method == "POST":
        producto_id = request.POST.get("producto")
        cantidad_vendida = float(request.POST.get("cantidad", 0))
        metodo_pago = request.POST.get("metodo_pago")
        monto_recibido = request.POST.get("monto_recibido")

        producto = get_object_or_404(Producto, id=producto_id)

        # 1. Validación de Stock Disponible 
       # 1. Validación de Stock Disponible 
        if producto.cantidad <= 0:
            messages.error(
                request,
                f"¡Producto agotado! {producto.nombre} no tiene stock disponible.",
            )
            return redirect("ventas")

        if cantidad_vendida > producto.cantidad:
            messages.error(
                request,
                f"¡Stock insuficiente! Solo quedan {producto.cantidad} unidades de {producto.nombre}.",
            )
            return redirect("ventas")

        subtotal = float(producto.precio_unitario) * cantidad_vendida

        # 2. Cálculo de vuelto para efectivo
        vuelto = 0.0
        if metodo_pago == "efectivo" and monto_recibido:
            monto_recibido = float(monto_recibido)
            if monto_recibido >= subtotal:
                vuelto = monto_recibido - subtotal

        # Guardar la transacción
        nueva_venta = Venta.objects.create(
            total=subtotal, metodo_pago=metodo_pago
        )

        DetalleVenta.objects.create(
            venta=nueva_venta,
            producto=producto,
            cantidad=cantidad_vendida,
            precio_unitario=producto.precio_unitario,
            subtotal=subtotal,
        )

        # Descontar stock
        producto.cantidad = float(producto.cantidad) - cantidad_vendida
        producto.save()

        # Feedback al usuario 
        if vuelto > 0:
            messages.success(
                request,
                f"Venta #{nueva_venta.id} registrada. ¡Entregar vuelto de ${vuelto:.2f}!",
            )
        else:
            messages.success(
                request, f"Venta #{nueva_venta.id} registrada con éxito."
            )

        return redirect("ventas")

# Métricas del Día
    hoy_local = timezone.localdate()
    ventas_hoy = Venta.objects.all()

    # Corregido: usamos alias explícito total=Sum("total") para que coincida ["total"]
    total_recaudado_hoy = ventas_hoy.aggregate(total=Sum("total"))["total"] or 0
    cantidad_ventas_hoy = ventas_hoy.count()
    ticket_promedio = (
        (total_recaudado_hoy / cantidad_ventas_hoy)
        if cantidad_ventas_hoy > 0
        else 0
    )

    productos = Producto.objects.all()
    ultimas_ventas = Venta.objects.all().order_by("-fecha")[:10]

    return render(
        request,
        "core/ventas.html",
        {
            "productos": productos,
            "ultimas_ventas": ultimas_ventas,
        
            "total_recaudado_hoy": total_recaudado_hoy,
            "cantidad_ventas_hoy": cantidad_ventas_hoy,
            "ticket_promedio": ticket_promedio,
            "total_recaudado": total_recaudado_hoy,  
            "cantidad_ventas": cantidad_ventas_hoy,   
        },
    )

@login_required
def eliminar_producto(request, id):
    producto = get_object_or_404(Producto, id=id)
    producto.delete()
    return redirect("inventario")


def salir(request):
    logout(request)
    return redirect("login")


# Editar
@login_required
def editar_producto(request, id):
    producto = get_object_or_404(Producto, id=id)

    if request.method == "POST":
        producto.nombre = request.POST.get("nombre")
        producto.cantidad = request.POST.get("cantidad")
        producto.unidad_medida = request.POST.get("unidad_medida")
        producto.precio_unitario = request.POST.get("precio_unitario")
        producto.stock_minimo = request.POST.get("stock_minimo")
        producto.save()
        return redirect("inventario")

    return render(request, "core/editar_producto.html", {"producto": producto})
