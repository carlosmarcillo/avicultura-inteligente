from django.urls import path
from . import views

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('usuarios/', views.usuarios_view, name='usuarios'),
    path('granjas/', views.granjas_view, name='granjas'),
    path('produccion/', views.produccion_view, name='produccion'),
    path('alimentacion/', views.alimentacion_view, name='alimentacion'),
    path('inventarios/', views.inventarios_view, name='inventarios'),
    path('finanzas/', views.finanzas_view, name='finanzas'),
    path('ambiente/', views.ambiente_view, name='ambiente'),
    path('reportes/', views.reportes_view, name='reportes'),
]
