from decimal import Decimal
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib import messages
from django.db.models import Sum
from .models import (
    PerfilUsuario, Granja, Lote, Produccion, Alimentacion,
    Insumo, MovimientoInventario, MovimientoFinanciero, CondicionAmbiental
)

def es_admin(user):
    if user.is_superuser:
        return True
    perfil = getattr(user, 'perfil', None)
    return perfil and perfil.rol == 'ADMIN'

def login_view(request):
    if request.user.is_authenticated:
        return redirect('dashboard')
    if request.method == 'POST':
        username = request.POST.get('username', '').strip()
        password = request.POST.get('password', '').strip()
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('dashboard')
        messages.error(request, 'Usuario o contraseña incorrectos.')
    return render(request, 'granjas/login.html')

def logout_view(request):
    logout(request)
    return redirect('login')

@login_required
def dashboard(request):
    total_granjas = Granja.objects.count()
    total_lotes = Lote.objects.filter(estado='ACTIVO').count()
    total_prod = Produccion.objects.aggregate(t=Sum('cantidad'))['t'] or 0
    ingresos = MovimientoFinanciero.objects.filter(tipo='INGRESO').aggregate(t=Sum('valor'))['t'] or 0
    gastos = MovimientoFinanciero.objects.filter(tipo='GASTO').aggregate(t=Sum('valor'))['t'] or 0
    context = {
        'total_granjas': total_granjas,
        'total_lotes': total_lotes,
        'total_prod': total_prod,
        'balance': ingresos - gastos,
        'ultimas_prod': Produccion.objects.select_related('lote')[:5],
        'insumos': Insumo.objects.all(),
        'es_admin': es_admin(request.user),
    }
    return render(request, 'granjas/dashboard.html', context)

@login_required
def usuarios_view(request):
    if not es_admin(request.user):
        messages.error(request, 'Acceso denegado: módulo exclusivo para Administrador (RNF02).')
        return redirect('dashboard')
    if request.method == 'POST':
        username = request.POST.get('username', '').strip()
        nombre = request.POST.get('first_name', '').strip()
        password = request.POST.get('password', '').strip()
        rol = request.POST.get('rol', 'PRODUCTOR')
        if not username or not password:
            messages.error(request, 'Todos los campos obligatorios deben completarse.')
        elif User.objects.filter(username=username).exists():
            messages.error(request, 'El identificador de usuario ya existe.')
        else:
            u = User.objects.create_user(username=username, first_name=nombre, password=password)
            PerfilUsuario.objects.create(user=u, rol=rol)
            messages.success(request, f'Usuario {username} creado con rol {rol}.')
            return redirect('usuarios')
    usuarios = User.objects.select_related('perfil').all()
    return render(request, 'granjas/usuarios.html', {'usuarios': usuarios, 'es_admin': True})

@login_required
def granjas_view(request):
    if request.method == 'POST':
        accion = request.POST.get('accion')
        if accion == 'crear_granja':
            nombre = request.POST.get('nombre', '').strip()
            ubicacion = request.POST.get('ubicacion', '').strip()
            if not nombre or not ubicacion:
                messages.error(request, 'Nombre y ubicación de la granja son obligatorios.')
            else:
                Granja.objects.create(nombre=nombre, ubicacion=ubicacion, responsable=request.user)
                messages.success(request, 'Granja registrada correctamente.')
        elif accion == 'crear_lote':
            granja_id = request.POST.get('granja_id')
            codigo = request.POST.get('codigo', '').strip()
            tipo = request.POST.get('tipo_produccion', 'PONEDORAS')
            aves = request.POST.get('cantidad_aves', '0')
            fecha = request.POST.get('fecha_inicio')
            if not granja_id or not codigo or not fecha or int(aves or 0) <= 0:
                messages.error(request, 'Complete todos los campos obligatorios del lote con valores válidos.')
            else:
                Lote.objects.create(
                    granja_id=granja_id, codigo=codigo, tipo_produccion=tipo,
                    cantidad_aves=int(aves), fecha_inicio=fecha
                )
                messages.success(request, 'Lote asociado correctamente.')
        return redirect('granjas')
    return render(request, 'granjas/granjas.html', {
        'granjas': Granja.objects.prefetch_related('lotes').all(),
        'es_admin': es_admin(request.user),
    })

@login_required
def produccion_view(request):
    if request.method == 'POST':
        lote_id = request.POST.get('lote_id')
        fecha = request.POST.get('fecha')
        cantidad = request.POST.get('cantidad', '0')
        obs = request.POST.get('observacion', '')
        if not lote_id or not fecha or int(cantidad or 0) <= 0:
            messages.error(request, 'Lote, fecha y cantidad mayor a 0 son obligatorios.')
        else:
            Produccion.objects.create(lote_id=lote_id, fecha=fecha, cantidad=int(cantidad), observacion=obs)
            messages.success(request, 'Registro de producción guardado.')
            return redirect('produccion')
    return render(request, 'granjas/produccion.html', {
        'lotes': Lote.objects.filter(estado='ACTIVO'),
        'registros': Produccion.objects.select_related('lote', 'lote__granja').all(),
        'es_admin': es_admin(request.user),
    })

@login_required
def alimentacion_view(request):
    if request.method == 'POST':
        lote_id = request.POST.get('lote_id')
        fecha = request.POST.get('fecha')
        tipo = request.POST.get('tipo_alimento', '').strip()
        cantidad = request.POST.get('cantidad', '0')
        unidad = request.POST.get('unidad', 'kg')
        if not lote_id or not fecha or not tipo or Decimal(cantidad or '0') <= 0:
            messages.error(request, 'Todos los campos obligatorios deben ser válidos y positivos.')
        else:
            Alimentacion.objects.create(
                lote_id=lote_id, fecha=fecha, tipo_alimento=tipo,
                cantidad=Decimal(cantidad), unidad=unidad
            )
            messages.success(request, 'Consumo de alimento registrado.')
            return redirect('alimentacion')
    return render(request, 'granjas/alimentacion.html', {
        'lotes': Lote.objects.filter(estado='ACTIVO'),
        'registros': Alimentacion.objects.select_related('lote', 'lote__granja').all(),
        'es_admin': es_admin(request.user),
    })

@login_required
def inventarios_view(request):
    if request.method == 'POST':
        accion = request.POST.get('accion')
        if accion == 'crear_insumo':
            nombre = request.POST.get('nombre', '').strip()
            categoria = request.POST.get('categoria', 'ALIMENTO')
            unidad = request.POST.get('unidad', 'kg').strip()
            inicial = Decimal(request.POST.get('existencia_inicial') or '0')
            if not nombre or inicial < 0:
                messages.error(request, 'Nombre obligatorio y existencia inicial no negativa.')
            else:
                Insumo.objects.create(nombre=nombre, categoria=categoria, unidad=unidad, existencia_inicial=inicial)
                messages.success(request, 'Insumo creado en catálogo.')
        elif accion == 'movimiento':
            insumo_id = request.POST.get('insumo_id')
            fecha = request.POST.get('fecha')
            tipo = request.POST.get('tipo')
            cantidad = Decimal(request.POST.get('cantidad') or '0')
            obs = request.POST.get('observacion', '')
            if not insumo_id or not fecha or cantidad <= 0:
                messages.error(request, 'Seleccione insumo, fecha y cantidad mayor a 0.')
            else:
                insumo = Insumo.objects.get(id=insumo_id)
                if tipo == 'SALIDA' and cantidad > insumo.existencia_actual:
                    messages.error(request, f'Existencia insuficiente ({insumo.existencia_actual} {insumo.unidad}).')
                else:
                    MovimientoInventario.objects.create(
                        insumo=insumo, fecha=fecha, tipo=tipo, cantidad=cantidad, observacion=obs
                    )
                    messages.success(request, 'Movimiento de inventario registrado.')
        return redirect('inventarios')
    return render(request, 'granjas/inventarios.html', {
        'insumos': Insumo.objects.all(),
        'movimientos': MovimientoInventario.objects.select_related('insumo').all()[:20],
        'es_admin': es_admin(request.user),
    })

@login_required
def finanzas_view(request):
    if request.method == 'POST':
        tipo = request.POST.get('tipo')
        fecha = request.POST.get('fecha')
        concepto = request.POST.get('concepto', '').strip()
        valor = Decimal(request.POST.get('valor') or '0')
        granja_id = request.POST.get('granja_id') or None
        if not fecha or not concepto or valor <= 0:
            messages.error(request, 'Fecha, concepto y valor mayor a 0 son obligatorios.')
        else:
            MovimientoFinanciero.objects.create(
                tipo=tipo, fecha=fecha, concepto=concepto, valor=valor, granja_id=granja_id
            )
            messages.success(request, 'Movimiento financiero registrado.')
            return redirect('finanzas')
    movs = MovimientoFinanciero.objects.select_related('granja').all()
    ingresos = movs.filter(tipo='INGRESO').aggregate(t=Sum('valor'))['t'] or 0
    gastos = movs.filter(tipo='GASTO').aggregate(t=Sum('valor'))['t'] or 0
    return render(request, 'granjas/finanzas.html', {
        'movimientos': movs,
        'granjas': Granja.objects.all(),
        'ingresos': ingresos,
        'gastos': gastos,
        'balance': ingresos - gastos,
        'es_admin': es_admin(request.user),
    })

@login_required
def ambiente_view(request):
    if request.method == 'POST':
        lote_id = request.POST.get('lote_id')
        fecha = request.POST.get('fecha')
        temp = request.POST.get('temperatura')
        hum = request.POST.get('humedad')
        obs = request.POST.get('observacion', '')
        if not lote_id or not fecha or not temp or not hum:
            messages.error(request, 'Todos los campos de medición ambiental son obligatorios.')
        else:
            CondicionAmbiental.objects.create(
                lote_id=lote_id, fecha=fecha, temperatura=Decimal(temp), humedad=Decimal(hum), observacion=obs
            )
            messages.success(request, 'Condición ambiental registrada.')
            return redirect('ambiente')
    return render(request, 'granjas/ambiente.html', {
        'lotes': Lote.objects.filter(estado='ACTIVO'),
        'registros': CondicionAmbiental.objects.select_related('lote', 'lote__granja').all(),
        'es_admin': es_admin(request.user),
    })

@login_required
def reportes_view(request):
    lote_id = request.GET.get('lote_id', '')
    fecha_inicio = request.GET.get('fecha_inicio', '')
    fecha_fin = request.GET.get('fecha_fin', '')

    prods = Produccion.objects.select_related('lote', 'lote__granja').all()
    alims = Alimentacion.objects.select_related('lote', 'lote__granja').all()
    finanzas = MovimientoFinanciero.objects.all()

    if lote_id:
        prods = prods.filter(lote_id=lote_id)
        alims = alims.filter(lote_id=lote_id)
    if fecha_inicio:
        prods = prods.filter(fecha__gte=fecha_inicio)
        alims = alims.filter(fecha__gte=fecha_inicio)
        finanzas = finanzas.filter(fecha__gte=fecha_inicio)
    if fecha_fin:
        prods = prods.filter(fecha__lte=fecha_fin)
        alims = alims.filter(fecha__lte=fecha_fin)
        finanzas = finanzas.filter(fecha__lte=fecha_fin)

    total_prod = prods.aggregate(t=Sum('cantidad'))['t'] or 0
    total_alim = alims.aggregate(t=Sum('cantidad'))['t'] or 0
    ingresos = finanzas.filter(tipo='INGRESO').aggregate(t=Sum('valor'))['t'] or 0
    gastos = finanzas.filter(tipo='GASTO').aggregate(t=Sum('valor'))['t'] or 0

    return render(request, 'granjas/reportes.html', {
        'lotes': Lote.objects.all(),
        'lote_id': lote_id,
        'fecha_inicio': fecha_inicio,
        'fecha_fin': fecha_fin,
        'prods': prods,
        'alims': alims,
        'insumos': Insumo.objects.all(),
        'total_prod': total_prod,
        'total_alim': total_alim,
        'ingresos': ingresos,
        'gastos': gastos,
        'balance': ingresos - gastos,
        'es_admin': es_admin(request.user),
    })
