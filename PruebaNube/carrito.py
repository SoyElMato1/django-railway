from .models import CarritoM , ItemCarrito
from django.contrib.auth.models import User
import uuid

class Carrito:
    def __init__(self, request):
        self.request = request
        self.session = request.session
        # Usar la session_key para identificar el carrito globalmente
        session_key = self.session.session_key
        
        # Obtener o crear el carrito asociado a la sesión
        carrito, creado = CarritoM.objects.get_or_create(session_key=session_key, cliente=None)
        self.carrito = carrito
        
        # Cargar los items del carrito en la sesión
        self.carito = self.carrito.items.all()  # Asegúrate de que esto esté correctamente definido


    def agregar(self, producto):
        producto_id = str(producto.codigo_producto)
        item, _ = ItemCarrito.objects.get_or_create(carrito=self.carrito, producto=producto)
        item.cantidad += 1
        item.save()
        self.carrito.save()

    def guardar_carrito(self):
        self.session.modified = True

    def eliminar(self, producto):
        ItemCarrito.objects.filter(carrito=self.carrito, producto=producto).delete()
    
    def restar(self, producto):
        item = ItemCarrito.objects.filter(carrito=self.carrito, producto=producto).first()
        if item:
            item.cantidad -= 1
            if item.cantidad <= 0:
                self.eliminar(producto)
            else:
                item.save()

    def limpiar(self):
        ItemCarrito.objects.filter(carrito=self.carrito).delete()


    def obtener_items(self):
        items = ItemCarrito.objects.filter(carrito=self.carrito)
        total = 0
        items_serializados = []

        for item in items:
            producto = item.producto
            cantidad = item.cantidad
            subtotal = producto.precio * cantidad
            total += subtotal
            items_serializados.append({
                'producto': producto,
                'cantidad': cantidad,
                'subtotal': subtotal,
            })

        return items_serializados, total