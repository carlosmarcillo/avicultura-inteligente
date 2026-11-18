from django.db import models
from django.contrib.auth.models import User
from django.db.models import Sum

class PerfilUsuario(models.Model):
    ROLES = [
        ('ADMIN', 'Administrador'),
        ('PRODUCTOR', 'Productor'),
    ]
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='perfil')
    rol = models.CharField(max_length=15, choices=ROLES, default='PRODUCTOR')
    activo = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.user.username} ({self.get_rol_display()})"

class Granja(models.Model):
    nombre = models.CharField(max_length=120)
    ubicacion = models.CharField(max_length=150, default='Villa Gorgona, Candelaria')
    responsable = models.ForeignKey(User, on_delete=models.CASCADE, related_name='granjas')

    def __str__(self):
        return self.nombre

class Lote(models.Model):
    TIPOS = [
        ('PONEDORAS', 'Aves Ponedoras'),
        ('ENGORDE', 'Pollo de Engorde'),
        ('LEVANTE', 'Levante'),
    ]
    ESTADOS = [
        ('ACTIVO', 'Activo'),
        ('CERRADO', 'Cerrado'),
    ]
    granja = models.ForeignKey(Granja, on_delete=models.CASCADE, related_name='lotes')
    codigo = models.CharField(max_length=50)
    tipo_produccion = models.CharField(max_length=20, choices=TIPOS, default='PONEDORAS')
    cantidad_aves = models.PositiveIntegerField(default=100)
    fecha_inicio = models.DateField()
    estado = models.CharField(max_length=15, choices=ESTADOS, default='ACTIVO')

    def __str__(self):
        return f"{self.codigo} - {self.granja.nombre}"

class Produccion(models.Model):
    lote = models.ForeignKey(Lote, on_delete=models.CASCADE, related_name='producciones')
    fecha = models.DateField()
    cantidad = models.PositiveIntegerField(help_text="Unidades de huevo o kg producidos")
    observacion = models.TextField(blank=True)

    class Meta:
        ordering = ['-fecha']

class Alimentacion(models.Model):
    lote = models.ForeignKey(Lote, on_delete=models.CASCADE, related_name='alimentaciones')
    fecha = models.DateField()
    tipo_alimento = models.CharField(max_length=100)
    cantidad = models.DecimalField(max_digits=10, decimal_places=2)
    unidad = models.CharField(max_length=20, default='kg')

    class Meta:
        ordering = ['-fecha']

class Insumo(models.Model):
    CATEGORIAS = [
        ('ALIMENTO', 'Alimento Balanceado'),
        ('MEDICAMENTO', 'Medicamentos y Vitaminas'),
        ('EMPAQUE', 'Cubetas y Empaques'),
        ('OTRO', 'Otros Insumos'),
    ]
    nombre = models.CharField(max_length=120)
    categoria = models.CharField(max_length=20, choices=CATEGORIAS, default='ALIMENTO')
    unidad = models.CharField(max_length=20, default='kg')
    existencia_inicial = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    @property
    def existencia_actual(self):
        entradas = self.movimientos.filter(tipo='ENTRADA').aggregate(t=Sum('cantidad'))['t'] or 0
        salidas = self.movimientos.filter(tipo='SALIDA').aggregate(t=Sum('cantidad'))['t'] or 0
        return self.existencia_inicial + entradas - salidas

    def __str__(self):
        return f"{self.nombre} ({self.existencia_actual} {self.unidad})"

class MovimientoInventario(models.Model):
    TIPOS = [
        ('ENTRADA', 'Entrada'),
        ('SALIDA', 'Salida'),
    ]
    insumo = models.ForeignKey(Insumo, on_delete=models.CASCADE, related_name='movimientos')
    fecha = models.DateField()
    tipo = models.CharField(max_length=10, choices=TIPOS)
    cantidad = models.DecimalField(max_digits=10, decimal_places=2)
    observacion = models.CharField(max_length=200, blank=True)

    class Meta:
        ordering = ['-fecha']

class MovimientoFinanciero(models.Model):
    TIPOS = [
        ('INGRESO', 'Ingreso'),
        ('GASTO', 'Gasto'),
    ]
    tipo = models.CharField(max_length=10, choices=TIPOS)
    fecha = models.DateField()
    concepto = models.CharField(max_length=150)
    valor = models.DecimalField(max_digits=12, decimal_places=2)
    granja = models.ForeignKey(Granja, on_delete=models.SET_NULL, null=True, blank=True)

    class Meta:
        ordering = ['-fecha']

class CondicionAmbiental(models.Model):
    lote = models.ForeignKey(Lote, on_delete=models.CASCADE, related_name='condiciones')
    fecha = models.DateField()
    temperatura = models.DecimalField(max_digits=5, decimal_places=2, help_text="°C")
    humedad = models.DecimalField(max_digits=5, decimal_places=2, help_text="%")
    observacion = models.TextField(blank=True)

    class Meta:
        ordering = ['-fecha']
