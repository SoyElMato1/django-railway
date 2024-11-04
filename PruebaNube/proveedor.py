from django.shortcuts import get_object_or_404
from .models import User, Proveedor
from django.core.files.base import ContentFile

def register_proveedor(data):
    foto = None
    if 'foto' in data:
        foto = ContentFile(data['foto'].read(), name=data['foto'].name)

    # Crear el usuario
    user = User.objects.create_proveedor(
        username=data['correo_electronico'],
        correo_user=data['correo_electronico'],
        rut=data['rut'],
        nom_user=data['nom_user'],
        ap_user=data['ap_user'],
        password=data['contrasena'],  # Usar la contraseña proporcionada
        rol='proveedor'  # Asignar el rol de proveedor
    )
    
    # Registrar al proveedor
    proveedor = Proveedor.objects.create(
        rut=data['rut'],
        dv=data['dv'],
        correo_electronico=data['correo_electronico'],
        contrasena=data['contrasena'],
        nombre=data['nom_user'],
        apellido=data['ap_user'],
        foto=foto
    )
    
    return user, proveedor
