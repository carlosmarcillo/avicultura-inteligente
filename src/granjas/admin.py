from django.contrib import admin
from .models import (
    PerfilUsuario, Granja, Lote, Produccion, Alimentacion,
    Insumo, MovimientoInventario, MovimientoFinanciero, CondicionAmbiental
)

admin.site.register(PerfilUsuario)
admin.site.register(Granja)
admin.site.register(Lote)
admin.site.register(Produccion)
admin.site.register(Alimentacion)
admin.site.register(Insumo)
admin.site.register(MovimientoInventario)
admin.site.register(MovimientoFinanciero)
admin.site.register(CondicionAmbiental)
