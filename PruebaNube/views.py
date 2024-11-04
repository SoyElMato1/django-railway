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
    
@csrf_exempt
@api_view(['GET', 'PUT', 'DELETE'])
@permission_classes([AllowAny])
def detalle_proveedor(request, id):
    """
    Recupera, actualiza o elimina un proveedor.
    """
    try: 
        proveedor = Proveedor.objects.get(rut=id) 
    except Proveedor.DoesNotExist: 
        return JsonResponse({'message': 'El proveedor no existe'}, status=status.HTTP_404_NOT_FOUND) 
    if request.method == 'GET': 
        proveedor_serializer = ProveedorSerializer(proveedor) 
        return JsonResponse(proveedor_serializer.data) 
    elif request.method == 'PUT': 
        proveedor_data = JSONParser().parse(request) 
        proveedor_serializer = ProveedorSerializer(proveedor, data=proveedor_data) 
        if proveedor_serializer.is_valid(): 
            proveedor_serializer.save() 
            return JsonResponse(proveedor_serializer.data) 
        return JsonResponse(proveedor_serializer.errors, status=status.HTTP_400_BAD_REQUEST) 
    elif request.method == 'DELETE': 
        proveedor.delete() 
        return JsonResponse({'message': 'Proveedor eliminado correctamente!'}, status=status.HTTP_204_NO_CONTENT)

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
# agregar_productos
@csrf_exempt
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def agregar_producto(request):
    """
    Agregar un nuevo producto.
    """
    if request.method == 'POST':
        producto_data = JSONParser().parse(request)
        producto_serializer = ProductoSerializer(data=producto_data)
        if producto_serializer.is_valid():
            rut_proveedor = request.POST.get('rut_proveedor')  # Obtener RUT del proveedor
            try:
                proveedor = Proveedor.objects.get(rut=rut_proveedor)
                categoria = Categoria.objects.get(id=producto_data.get('categoria'))  # Obtener la categoría
                producto_serializer.save(id_proveedor=proveedor, categoria=categoria)  # Guarda el producto con el proveedor y categoría
                return JsonResponse(producto_serializer.data, status=status.HTTP_201_CREATED)
            except (Proveedor.DoesNotExist, Categoria.DoesNotExist):
                return JsonResponse({"error": "Proveedor o categoría no encontrados"}, status=status.HTTP_404_NOT_FOUND)
        return JsonResponse(producto_serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@csrf_exempt
@api_view(['PUT', 'DELETE'])
@permission_classes([IsAuthenticated])  # Requiere autenticación
def actualizar_eliminar_producto(request, id):
    """
    Modificar o eliminar un producto específico.
    """
    try:
        producto = Producto.objects.get(codigo_producto=id)
    except Producto.DoesNotExist:
        return HttpResponse(status=status.HTTP_404_NOT_FOUND)

    if request.method == 'PUT':
        producto_data = JSONParser().parse(request)
        producto_serializer = ProductoSerializer(producto, data=producto_data)
        if producto_serializer.is_valid():
            producto_serializer.save()
            return JsonResponse(producto_serializer.data)
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

#------------------------Vista Transbank--------------------------------------

@api_view(['POST'])
@permission_classes([AllowAny])
def iniciar_pago(request):
    try:
        # Obtener el cuerpo de la solicitud y extraer el 'total'
        data = json.loads(request.body)
        total = data.get('total', 0)  # Captura el 'total', predeterminado a 0 si no existe

        # Validación del monto
        if total <= 0:
            return JsonResponse({'success': False, 'message': 'Monto no válido'}, status=400)

        # Procesar la transacción si el monto es válido
        options = WebpayOptions(
            commerce_code='597055555532',
            api_key='579B532A7440BB0C9079DED94D31EA1615BACEB56610332264630D42D0A36B1C',
        )
        tx = Transaction(options)
        response = tx.create(buy_order='order12345', session_id='session12345', amount=total, return_url='http://127.0.0.1:8000/modelo/pago_exitoso/')

        return JsonResponse({'success': True, 'transaction_url': response['url'], 'token': response['token']})

    except Exception as e:
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
        response = Transaction().commit(token_ws)
        print("Response de Transbank:", response)  # Verificar la respuesta de Transbank

        if response['status'] == 'AUTHORIZED':
            # Redirigir a la ruta de Angular con el resultado de la transacción
            return redirect(f'http://localhost:4200/pago-exitoso?order={response}')
        else:
            return redirect('pago_fallido')

    except Exception as e:
        print("Error durante el procesamiento del pago:", str(e))  # Registro del error
        return JsonResponse({'success': False, 'error': str(e)})

@permission_classes([AllowAny])
def pago_fallido(request):
    # Aquí puedes hacer cualquier lógica que necesites antes de redirigir
    return redirect('http://localhost:4200/pago-fallido?message=El%20pago%20fue%20cancelado%20o%20fallido.%20Int%C3%A9ntalo%20de%20nuevo.')

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