from datetime import date, timedelta
from decimal import Decimal
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from granjas.models import (
    PerfilUsuario, Granja, Lote, Produccion, Alimentacion,
    Insumo, MovimientoInventario, MovimientoFinanciero, CondicionAmbiental
)

class Command(BaseCommand):
    help = 'Carga datos iniciales de prueba para Avicultura Inteligente (TRL5)'

    def handle(self, *args, **kwargs):
        admin_user, created = User.objects.get_or_create(
            username='admin',
            defaults={'first_name': 'Carlos Marcillo (Admin)', 'is_staff': True, 'is_superuser': True}
        )
        admin_user.set_password('Admin2026!')
        admin_user.save()
        PerfilUsuario.objects.get_or_create(user=admin_user, defaults={'rol': 'ADMIN'})

        prod_user, created = User.objects.get_or_create(
            username='productor',
            defaults={'first_name': 'Avicultor Villa Gorgona'}
        )
        prod_user.set_password('Productor2026!')
        prod_user.save()
        PerfilUsuario.objects.get_or_create(user=prod_user, defaults={'rol': 'PRODUCTOR'})

        g1, _ = Granja.objects.get_or_create(
            nombre='Granja Avícola El Porvenir',
            defaults={'ubicacion': 'Vereda Villa Gorgona, Candelaria', 'responsable': prod_user}
        )
        g2, _ = Granja.objects.get_or_create(
            nombre='Granja Santa Elena',
            defaults={'ubicacion': 'Sector Central, Villa Gorgona', 'responsable': admin_user}
        )

        hoy = date.today()
        l1, _ = Lote.objects.get_or_create(
            codigo='LOTE-PON-01',
            granja=g1,
            defaults={'tipo_produccion': 'PONEDORAS', 'cantidad_aves': 450, 'fecha_inicio': hoy - timedelta(days=60)}
        )
        l2, _ = Lote.objects.get_or_create(
            codigo='LOTE-ENG-02',
            granja=g2,
            defaults={'tipo_produccion': 'ENGORDE', 'cantidad_aves': 300, 'fecha_inicio': hoy - timedelta(days=25)}
        )

        if not Produccion.objects.exists():
            Produccion.objects.create(lote=l1, fecha=hoy - timedelta(days=2), cantidad=395, observacion='Postura normal mañana')
            Produccion.objects.create(lote=l1, fecha=hoy - timedelta(days=1), cantidad=402, observacion='Excelente rendimiento')
            Produccion.objects.create(lote=l2, fecha=hoy - timedelta(days=1), cantidad=620, observacion='Pesaje parcial en kg')

        if not Alimentacion.objects.exists():
            Alimentacion.objects.create(lote=l1, fecha=hoy - timedelta(days=1), tipo_alimento='Concentrado Ponedora Fase 1', cantidad=Decimal('52.50'), unidad='kg')
            Alimentacion.objects.create(lote=l2, fecha=hoy - timedelta(days=1), tipo_alimento='Engorde Finalizador', cantidad=Decimal('45.00'), unidad='kg')

        ins1, _ = Insumo.objects.get_or_create(
            nombre='Concentrado Ponedora Fase 1',
            defaults={'categoria': 'ALIMENTO', 'unidad': 'kg', 'existencia_inicial': Decimal('500.00')}
        )
        ins2, _ = Insumo.objects.get_or_create(
            nombre='Cubetas de cartón x30',
            defaults={'categoria': 'EMPAQUE', 'unidad': 'unidades', 'existencia_inicial': Decimal('200.00')}
        )
        if not MovimientoInventario.objects.exists():
            MovimientoInventario.objects.create(insumo=ins1, fecha=hoy - timedelta(days=3), tipo='ENTRADA', cantidad=Decimal('200.00'), observacion='Compra proveedor local')
            MovimientoInventario.objects.create(insumo=ins1, fecha=hoy - timedelta(days=1), tipo='SALIDA', cantidad=Decimal('52.50'), observacion='Consumo LOTE-PON-01')

        if not MovimientoFinanciero.objects.exists():
            MovimientoFinanciero.objects.create(tipo='INGRESO', fecha=hoy - timedelta(days=2), concepto='Venta 13 cubetas de huevo AA', valor=Decimal('234000'), granja=g1)
            MovimientoFinanciero.objects.create(tipo='GASTO', fecha=hoy - timedelta(days=3), concepto='Compra 5 bultos concentrado', valor=Decimal('425000'), granja=g1)
            MovimientoFinanciero.objects.create(tipo='INGRESO', fecha=hoy - timedelta(days=1), concepto='Venta lote pollo en pie', valor=Decimal('890000'), granja=g2)

        if not CondicionAmbiental.objects.exists():
            CondicionAmbiental.objects.create(lote=l1, fecha=hoy - timedelta(days=1), temperatura=Decimal('26.4'), humedad=Decimal('68.0'), observacion='Ventilación natural adecuada')
            CondicionAmbiental.objects.create(lote=l2, fecha=hoy, temperatura=Decimal('27.8'), humedad=Decimal('71.5'), observacion='Medición mediodía')

        self.stdout.write(self.style.SUCCESS('Datos de prueba de Avicultura Inteligente cargados exitosamente.'))
