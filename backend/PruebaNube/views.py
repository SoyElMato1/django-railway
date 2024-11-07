from django.conf import settings
from django.shortcuts import get_object_or_404, redirect, render
from django.http import HttpResponse, JsonResponse
from rest_framework.parsers import JSONParser
from rest_framework.response import Response
from .models import *
from .serializers import *
from django.views.decorators.csrf import csrf_exempt
from rest_framework.decorators import api_view, permission_classes, authentication_classes
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.authentication import TokenAuthentication 
from django.contrib.auth import authenticate, login
from rest_framework.authtoken.models import Token
import json
from django.contrib.auth import logout
from .proveedor import register_proveedor
from transbank.webpay.webpay_plus.transaction import Transaction, WebpayOptions
from transbank.common.integration_type import IntegrationType
from django.shortcuts import get_object_or_404
from django.core.files.base import ContentFile
import base64
from django.conf import settings
from django.core.files import File
import os
from django.utils.dateparse import parse_datetime
import uuid
import logging

# import openai

# Create your views here.

# ---------------------------------------Proveedor---------------------------------------------
@csrf_exempt
@api_view(['GET'])
@permission_classes([AllowAny])
def Ver_proveedor(request):
    if request.method == 'GET':
        proveedores = Proveedor.objects.all()
        serializer = ProveedorSerializer(proveedores, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

@csrf_exempt
@api_view(['GET', 'PUT'])
@permission_classes([IsAuthenticated])  # Asegura que solo los usuarios autenticados puedan acceder
def proveedor_detalle(request, id):
    try:
        proveedor = Proveedor.objects.get(rut=id)
    except Proveedor.DoesNotExist:
        return Response({"error": "Proveedor no encontrado"}, status=404)

    if request.method == 'GET':
        serializer = ProveedorSerializer(proveedor)
        return Response(serializer.data)
    elif request.method == 'PUT':
        serializer = ProveedorSerializer(proveedor, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=400)

# -----------------------------------------Vista de Producto---------------------------------------------
@csrf_exempt
@api_view(['GET'])
@permission_classes([AllowAny])
def producto(request):
    """
    Lista de productos, o crea un nuevo producto.
    """
    if request.method == 'GET':
        productos = Producto.objects.all()
        serializer = ProductoSerializer(productos, many=True)
        return JsonResponse(serializer.data, safe=False)
@csrf_exempt
@api_view(['POST'])
@permission_classes([AllowAny])
def agregar_productos(request):
    if request.method == 'POST':
        productos_data = JSONParser().parse(request)
        productos_serializer = ProductoSerializer(data=productos_data)
        if productos_serializer.is_valid():
            productos_serializer.save()
            return JsonResponse(productos_serializer.data, status=status.HTTP_201_CREATED)
        return JsonResponse(productos_serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# Todos los productos de un Proveedor
@csrf_exempt
@api_view(['GET'])
@permission_classes([IsAuthenticated])  # Requiere autenticación
def obtener_productos(request):
    """
    Lista productos por el RUT del proveedor o agrega un nuevo producto.
    """
    # Filtrar productos por el RUT del proveedor
    if request.method == 'GET':
        rut_proveedor = request.GET.get('rut')
        
        if rut_proveedor:
            try:
                proveedor = Proveedor.objects.get(rut=rut_proveedor)
                productos = Producto.objects.filter(id_proveedor=proveedor)
            except Proveedor.DoesNotExist:
                return JsonResponse({"error": "Proveedor no encontrado"}, status=status.HTTP_404_NOT_FOUND)
        else:
            productos = Producto.objects.all()
        
        serializer = ProductoSerializer(productos, many=True)
        return JsonResponse(serializer.data, safe=False)

# Trae el producto del proveedor
@csrf_exempt
@api_view(["GET"])
@permission_classes([AllowAny])
def producto_proveedor(request, id):
    if request.method == "GET":
        producto = get_object_or_404(Producto, codigo_producto=id)
        producto_data = {
            'codigo_producto': producto.codigo_producto,
            'nombre_producto': producto.nombre_producto,
            'precio': producto.precio,
            'imagen_producto': producto.imagen_producto.url,
            'descripcion': producto.descripcion,
            'id_categoria': producto.id_categoria.id_categoria,
            'id_proveedor': producto.id_proveedor.rut
        }
        return JsonResponse(producto_data, status=200)
    else:
        return JsonResponse({'error': 'Método no permitido'}, status=405)
    
# Agregar Producto
@csrf_exempt
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def agregar_producto(request):
    if request.method == 'POST':
        producto_data = request.data.get('producto')
        rut_proveedor = request.data.get('rut_proveedor')
        # Verificar si producto_data y rut_proveedor existen
        if not producto_data or not rut_proveedor:
            return JsonResponse({"error": "Datos incompletos: 'producto' o 'rut_proveedor' no proporcionados"},
                                status=status.HTTP_400_BAD_REQUEST)
        try:
            proveedor = Proveedor.objects.get(rut=rut_proveedor)
        except Proveedor.DoesNotExist:
            return JsonResponse({"error": "Proveedor no encontrado"}, status=status.HTTP_404_NOT_FOUND)
        try:
            categoria = Categoria.objects.get(id_categoria=producto_data.get('id_categoria'))
        except Categoria.DoesNotExist:
            return JsonResponse({"error": "Categoría no encontrada"}, status=status.HTTP_404_NOT_FOUND)
        # Asignar los valores de proveedor y categoría al producto
        producto_data['id_proveedor'] = proveedor.rut
        producto_data['id_categoria'] = categoria.id_categoria
        if 'imagen_producto' in producto_data:
            imagen_data = producto_data.pop('imagen_producto')
            format, imgstr = imagen_data.split(';base64,')
            print(imagen_data)
            ext = format.split('/')[-1]
            imagen_file = ContentFile(base64.b64decode(imgstr), name=f'producto.{ext}')
            producto_data['imagen_producto'] = imagen_file
        producto_serializer = ProductoSerializer(data=producto_data)
        if producto_serializer.is_valid():
            producto_serializer.save()
            return JsonResponse(producto_serializer.data, status=status.HTTP_201_CREATED)
        return JsonResponse(producto_serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@csrf_exempt
@api_view(['PUT', 'DELETE'])
@permission_classes([IsAuthenticated])
def actualizar_eliminar_producto(request, id):
    try:
        producto = Producto.objects.get(codigo_producto=id)
    except Producto.DoesNotExist:
        return HttpResponse(status=status.HTTP_404_NOT_FOUND)
    if request.method == 'PUT': 
        producto_data = request.data.get('producto', {}).copy()
        if 'imagen_producto' in producto_data:
            imagen_data = producto_data.pop('imagen_producto')
            if imagen_data.startswith('/media/'):
                imagen_path = os.path.join(settings.MEDIA_ROOT, imagen_data.lstrip('/'))
                if os.path.exists(imagen_path):
                    with open(imagen_path, 'rb') as image_file:
                        imagen_file_django = File(image_file, name=os.path.basename(imagen_path))
                        producto_data['imagen_producto'] = imagen_file_django
            else:
                format, imgstr = imagen_data.split(';base64,')
                ext = format.split('/')[-1]
                imagen_file = ContentFile(base64.b64decode(imgstr), name=f'producto.{ext}')
                producto_data['imagen_producto'] = imagen_file
        producto_serializer = ProductoSerializer(producto, data=producto_data, partial=True)
        if producto_serializer.is_valid():
            producto_serializer.save()
            return JsonResponse(producto_serializer.data, status=status.HTTP_200_OK)
        return JsonResponse(producto_serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    elif request.method == 'DELETE':
        producto.delete()
        return HttpResponse(status=status.HTTP_204_NO_CONTENT)
    
# -------------------------------- Vista de Categoría ---------------------------------------------
@csrf_exempt
@api_view(['GET', 'POST'])
@permission_classes([AllowAny])
def get_categoria(request):
    """
    Lista de categorías, o crea una nueva categoría.
    """
    if request.method == 'GET':
        categorias = Categoria.objects.all()
        serializer = CategoriaSerializer(categorias, many=True)
        return JsonResponse(serializer.data, safe=False)
    elif request.method == 'POST':
        categoria_data = JSONParser().parse(request)
        categoria_serializer = CategoriaSerializer(data=categoria_data)
        if categoria_serializer.is_valid():
            categoria_serializer.save()
            return JsonResponse(categoria_serializer.data, status=status.HTTP_201_CREATED)
        return JsonResponse(categoria_serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@csrf_exempt
@api_view(['PUT', 'DELETE'])
@permission_classes([AllowAny])
def detalle_categoria(request, id):
    """
    Actualiza o elimina una categoría.
    """
    try:
        categoria = Categoria.objects.get(id_categoria=id)
    except Categoria.DoesNotExist:
        return HttpResponse(status=status.HTTP_404_NOT_FOUND)
    
    if request.method == 'PUT':
        categoria_data = JSONParser().parse(request)
        categoria_serializer = CategoriaSerializer(categoria, data=categoria_data)
        if categoria_serializer.is_valid():
            categoria_serializer.save()
            return JsonResponse(categoria_serializer.data)
        return JsonResponse(categoria_serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    elif request.method == 'DELETE':
        categoria.delete()
        return HttpResponse(status=status.HTTP_204_NO_CONTENT)
    

# -------------------------Vista de Login------------------------------------
@csrf_exempt
@permission_classes([AllowAny])
def login_view(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)  # Asegúrate de recibir el cuerpo de la solicitud como JSON
            username = data.get('username')
            password = data.get('password')

            if username is None or password is None:
                return JsonResponse({'error': 'Username and password are required'}, status=400)

            user = authenticate(request, username=username, password=password)
            if user is not None:
                token, created = Token.objects.get_or_create(user=user)

                login(request, user)
                return JsonResponse({
                    'token': token.key,
                    'user': {
                        'rol': user.rol
                    }
                })
            else:
                return JsonResponse({'error': 'Invalid credentials'}, status=400)

        except json.JSONDecodeError:
            return JsonResponse({'error': 'Invalid JSON'}, status=400)

    return JsonResponse({'error': 'Invalid request method'}, status=405)

@csrf_exempt  # Solo temporalmente para pruebas, no en producción
@permission_classes([AllowAny])
def logout_view(request):
    if request.method == 'POST':
        try:
            # Obtiene el token de la cabecera de la solicitud
            token = request.META.get('HTTP_AUTHORIZATION').split()[1]  # Expectativa de que sea un token de tipo 'Token <token>'
            token_instance = Token.objects.get(key=token)
            token_instance.delete()  # Elimina el token de la base de datos

            logout(request)  # Cierra la sesión del usuario
            return JsonResponse({'message': 'Logged out successfully'})
        except (Token.DoesNotExist, IndexError):
            return JsonResponse({'error': 'Invalid token'}, status=400)

    return JsonResponse({'error': 'Invalid request method'}, status=405)

@csrf_exempt
@api_view(['POST'])
@permission_classes([AllowAny])
def register_proveedor_view(request):
    if request.method == 'POST':
        data = request.data
        user, proveedor = register_proveedor(data)
        return Response({'message': 'Proveedor registrado exitosamente', 'user': str(user)}, status=status.HTTP_201_CREATED)
    return Response({'error': 'Método no permitido'}, status=status.HTTP_405_METHOD_NOT_ALLOWED)

#------------------------Vista Transbank---------------------------------------
logger = logging.getLogger(__name__)
@api_view(['POST'])
@permission_classes([AllowAny])
# Configura el logger


def iniciar_pago(request):
    try:
        # Obtener el cuerpo de la solicitud y extraer el 'total'
        data = json.loads(request.body)
        total = data.get('total', 0)  # Captura el 'total', predeterminado a 0 si no existe

        # Validación del monto
        if total <= 0:
            return JsonResponse({'success': False, 'message': 'Monto no válido'}, status=400)

        # Generar valores únicos para buy_order y session_id
        buy_order = str(uuid.uuid4())[:26]  # Limitar a 26 caracteres
        session_id = str(uuid.uuid4())[:26]  # Limitar a 26 caracteres

        # Procesar la transacción si el monto es válido
        options = WebpayOptions(
            commerce_code='597055555532',
            api_key='579B532A7440BB0C9079DED94D31EA1615BACEB56610332264630D42D0A36B1C',
        )
        tx = Transaction(options)
        response = tx.create(buy_order=buy_order, session_id=session_id, amount=total, return_url='http://127.0.0.1:8000/modelo/pago_exitoso/')

        return JsonResponse({'success': True, 'transaction_url': response['url'], 'token': response['token']})

    except Exception as e:
        logger.error(f'Error al iniciar pago: {str(e)}')  # Registrar el error
        return JsonResponse({'success': False, 'error': str(e)}, status=500)

@api_view(['POST'])
@permission_classes([AllowAny])
def validar_pago(request):
    token_ws = request.POST.get('token_ws')
    if not token_ws:
        return JsonResponse({'success': False, 'message': 'Token no proporcionado'}, status=400)

    try:
        # Configurar las opciones de Transbank
        options = WebpayOptions(
            commerce_code='597055555532',
            api_key='579B532A7440BB0C9079DED94D31EA1615BACEB56610332264630D42D0A36B1C'
        )

        tx = Transaction(options)
        response = tx.commit(token_ws)

        # Validar el estado de la transacción
        if response['status'] == 'AUTHORIZED':
            return JsonResponse({'success': True, 'message': 'Pago autorizado correctamente'})
        else:
            return JsonResponse({'success': False, 'message': f"Transacción no autorizada, estado: {response['status']}"})

    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=500)

@permission_classes([AllowAny])
def pago_exitoso(request):
    token_ws = request.GET.get('token_ws')

    if not token_ws:
        return JsonResponse({'success': False, 'message': 'Token no proporcionado'})

    try:
        # Commit de la transacción en Transbank
        response = Transaction().commit(token_ws)
        print("Response de Transbank:", response)  # Verificar la respuesta de Transbank

        if response['status'] == 'AUTHORIZED':
            # Extraer datos necesarios para guardar la transacción
            monto = response['amount']
            fecha = parse_datetime(response['transaction_date'])  # Guarda fecha y hora
            metodo_pago_code = response['payment_type_code']

            # Crear y guardar la nueva transacción sin utilizar el modelo MetodoPago
            nueva_transaccion = transaccion(
                metodo_pago=metodo_pago_code,  # Guardamos directamente el código del método de pago
                amount=monto,
                buy_order=response['buy_order'],
                status=response['status'],
                session_id=response['session_id'],
                transaction_date=fecha
            )
            nueva_transaccion.save()

            # Redirigir a la ruta de Angular con el resultado de la transacción
            return redirect(f'http://localhost:8100/pago-exitoso?order={response["buy_order"]}')
        else:
            # En caso de que la transacción no sea autorizada
            return redirect('pago_fallido')

    except Exception as e:  # Captura errores generales
        print("Error durante el procesamiento del pago:", str(e))  # Registro del error
        return JsonResponse({'success': False, 'error': str(e)})




def procesar_pago(request):
    # Suponiendo que tienes la respuesta de Transbank como un diccionario `response`
    response = {
        'payment_type_code': 'VD',  # Ejemplo de respuesta de Transbank
        'amount': 3500,
        'buy_order': 'order12345',
        'status': 'AUTHORIZED',
        'session_id': 'session12345',
        'transaction_date': '2024-11-04T23:48:39.707Z'
        # otros campos necesarios
    }

    # Crear una instancia de Transaccion con el método de pago y otros datos
    transaccion = transaccion(
        metodo_pago=response.get('payment_type_code'),  # Guarda el tipo de pago 'VD', 'VN', etc.
        amount=response.get('amount'),
        buy_order=response.get('buy_order'),
        status=response.get('status'),
        session_id=response.get('session_id'),
        transaction_date=response.get('transaction_date')
    )

    try:
        transaccion.save()
        print("Transacción guardada correctamente.")
    except Exception as e:
        print(f"Error durante el procesamiento del pago: {e}")

    # Resto de tu lógica de respuesta
    return render(request, 'pago_exitoso.html')

def detalles_pago_exitoso(request):
    buy_order = request.GET.get('order')

    if not buy_order:
        return JsonResponse({'success': False, 'message': 'Order ID no proporcionado'}, status=400)

    try:
        # Buscar la transacción por buy_order
        transaccion_obj = transaccion.objects.get(buy_order=buy_order)

        # Serializar los datos de la transacción
        data = {
            'metodo_pago': transaccion_obj.metodo_pago,  # Método de pago (código de Transbank)
            'amount': transaccion_obj.amount,
            'buy_order': transaccion_obj.buy_order,
            'status': transaccion_obj.status,
            'session_id': transaccion_obj.session_id,
            'transaction_date': transaccion_obj.transaction_date.strftime('%Y-%m-%d %H:%M:%S'),
        }

        return JsonResponse({'success': True, 'data': data})

    except transaccion.DoesNotExist:
        return JsonResponse({'success': False, 'message': 'Transacción no encontrada'}, status=404)


#def pago_exitoso(request):
#    token_ws = request.GET.get('token_ws')
#
 #   if not token_ws:
  #      return JsonResponse({'success': False, 'message': 'Token no proporcionado'})
#
 #   try:
  #      response = Transaction().commit(token_ws)
   #     print("Response de Transbank:", response)  # Verificar la respuesta de Transbank
#
 #       if response['status'] == 'AUTHORIZED':
  #          # Redirigir a la ruta de Angular con el resultado de la transacción
   #         return redirect(f'http://localhost:4200/pago-exitoso?order={response}')
    #    else:
     #       return redirect('pago_fallido')
#
 #   except Exception as e:
  #      print("Error durante el procesamiento del pago:", str(e))  # Registro del error
   #     return JsonResponse({'success': False, 'error': str(e)})

@permission_classes([AllowAny])
def pago_fallido(request):
    # Aquí puedes hacer cualquier lógica que necesites antes de redirigir
    return redirect('http://localhost:8100/pago-fallido?message=El%20pago%20fue%20cancelado%20o%20fallido.%20Int%C3%A9ntalo%20de%20nuevo.')

# -------------------------- Cliente -----------------------------
@csrf_exempt
@permission_classes([AllowAny])
def cliente_obtener(request, rut):
    cliente = get_object_or_404(Cliente, rut=rut) 
    response_data = {
        'dv': cliente.dv,
        'correo_electronico': cliente.correo_electronico,
        'nombre': cliente.nombre,
        'direccion': cliente.direccion,
    }
    return JsonResponse(response_data)
        
@csrf_exempt
@api_view(['POST'])
@permission_classes([AllowAny])
def guardar_cliente(request):
    if request.method == 'POST':
        cliente_data = JSONParser().parse(request)
        cliente_serializer = ClienteSerializer(data=cliente_data)
        
        if cliente_serializer.is_valid():
            cliente_serializer.save()
            return JsonResponse(cliente_serializer.data, status=status.HTTP_201_CREATED)
        
        return JsonResponse(cliente_serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    return JsonResponse({'error': 'Método no permitido'}, status=405)