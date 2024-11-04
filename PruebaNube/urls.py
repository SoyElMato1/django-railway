from django.urls import path
from .views import *
from .views_carrito import *


urlpatterns = [

#Producto
    path('producto/', producto, name='producto'),
    path('agregarPro/', agregar_productos, name='producto añadido'),
    path('categoria/', get_categoria, name='categoria'),

    path('productos/', obtener_productos, name='obtener_productos'),
    path('agreproductos/', agregar_producto, name='agregar_productos'),
    path('productos/<int:id>/', actualizar_eliminar_producto, name='actualizar_eliminar_producto'),

#Proveedor
    path('provee/', Ver_proveedor, name='proveedor'),
    path('provee/<int:id>/', detalle_proveedor, name='detalle_proveedores'),
    path('proveedores/<int:id>/', proveedor_detalle, name='proveedor_detalle'),

# Carrito
    path('agregar/<int:producto_id>/', agregar_al_carrito, name='agregar_al_carrito'),
    path('restar/<int:producto_id>/', restar_producto, name='restar producto'),
    path('limpiar/', limpiar_carrito, name= 'limpiar_carrito'),
    path('carrito/', ver_carrito, name='ver_carrito'),
    path('checkout/', checkout, name='checkout'),
    path('eliminar/<int:producto_id>/', eliminar_del_carrito, name='eliminar del carrito'),

# Cliente
    path('cliente/<int:rut>', cliente_obtener, name='obtener_al_cliente'),
    path('clienteAgre/', guardar_cliente, name='guardar_cliente'),

# Transbank
    path('pago/iniciar/', iniciar_pago, name='iniciar_pago'),
    path('validar_pago/', validar_pago, name='validar_pago'),
    path('pago_exitoso/', pago_exitoso, name='pago_exitoso'),
    path('pago_fallido/', pago_fallido, name='pago_fallido'),

#Login 
    path('login/', login_view, name='admin_login'),
    path('logout/', logout_view, name='logout'),
    path('registro_proveedor/', register_proveedor_view, name='registro proveedor'),


]