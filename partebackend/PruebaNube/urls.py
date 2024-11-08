from django.urls import path
from .views import *
from .views_carrito import *


urlpatterns = [

# Views Categoria
    path('categoria/', get_categoria, name='categoria'),

# Views Producto
    path('producto/', producto, name='producto'),
    path('agregarPro/', agregar_productos, name='producto añadido'),
    
    path('productos/', obtener_productos, name='obtener_productos'),
    path('producto/<int:id>/', producto_proveedor, name='obtener_producto'),
    path('agreproducto/', agregar_producto, name='producto añadido'),
    path('productos/<int:id>/', actualizar_eliminar_producto, name='actualizar_eliminar_producto'),

#Proveedor
    path('provee/', Ver_proveedor, name='proveedor'),
    path('proveedores/<int:id>/', proveedor_detalle, name='proveedor_detalle'),

# Carrito
    path('agregar/<int:producto_id>/', agregar_al_carrito, name='agregar_al_carrito'),
    path('restar/<int:producto_id>/', restar_producto, name='restar producto'),
    path('limpiar/', limpiar_carrito, name= 'limpiar_carrito'),
    path('carrito/', ver_carrito, name='ver_carrito'),
    path('crear_oden/', checkout, name='checkout'),
    path('eliminar/<int:producto_id>/', eliminar_del_carrito, name='eliminar del carrito'),

# Cliente
    path('cliente/<int:rut>', cliente_obtener, name='cliente_obtener'),
    path('clienteAgre/', guardar_cliente, name='guardar_cliente'),

# Transbank
    path('pago/iniciar/', iniciar_pago, name='iniciar_pago'),
    path('validar_pago/', validar_pago, name='validar_pago'),
    path('pago_exitoso/', pago_exitoso, name='pago_exitoso'),
    path('pago_fallido/', pago_fallido, name='pago_fallido'),
    path('detalles-pago-exitoso/', detalles_pago_exitoso, name='detalles_pago_exitoso'),
#Login 
    path('login/', login_view, name='admin_login'),
    path('logout/', logout_view, name='logout'),
    path('registro_proveedor/', register_proveedor_view, name='registro proveedor'),


]