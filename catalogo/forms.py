import re
from django import forms
from .models import Producto, Usuario
from django.contrib.auth import authenticate
from django.core.exceptions import ValidationError
from django.core.validators import RegexValidator
from django.contrib.auth.forms import PasswordChangeForm

# Formulario para la gestión de productos
class ProductoForm(forms.ModelForm):
    class Meta:
        model = Producto
        fields = ['nombre', 'descripcion', 'precio', 'stock', 'categoria', 'imagen']
        widgets = {
            'descripcion': forms.Textarea(attrs={'rows': 3}),
        }
        
#------------------------------------------------------------------------------------------------------
#---------------  CLASE PARA EL FORMULARIO DE REGISTRO CLIENTE (registro.html) -----------------------
#------------------------------------------------------------------------------------------------------
class RegistroForm(forms.ModelForm):
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Ingrese una contraseña',
        }),
        min_length=8,
        help_text="La contraseña debe tener al menos 8 caracteres, incluir letras y números.",
    )
    confirm_password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Confirme su contraseña',
        }),
        label="Confirmar contraseña",
    )

    telefono = forms.CharField(
        required=False,
        validators=[
            RegexValidator(
                regex=r'^\+?\d{7,15}$',
                message="El número de teléfono debe contener entre 7 y 15 dígitos, opcionalmente con un prefijo '+'.",
            )
        ],
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Ingrese su teléfono (opcional)',
        }),
    )

    class Meta:
        model = Usuario
        fields = ['nombre', 'email', 'direccion', 'telefono', 'password']
        widgets = {
            'nombre': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ingrese su nombre',
            }),
            'email': forms.EmailInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ingrese su correo electrónico',
            }),
            'direccion': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ingrese su dirección (opcional)',
            }),
        }

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if Usuario.objects.filter(email=email).exists():
            raise ValidationError("Este correo electrónico ya está registrado.")
        return email

    def clean_password(self):
        password = self.cleaned_data.get('password')
        if not any(char.isdigit() for char in password):
            raise ValidationError("La contraseña debe contener al menos un número.")
        if not any(char.isalpha() for char in password):
            raise ValidationError("La contraseña debe contener al menos una letra.")
        return password

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get('password')
        confirm_password = cleaned_data.get('confirm_password')

        if password and confirm_password and password != confirm_password:
            self.add_error('confirm_password', "Las contraseñas no coinciden.")
        return cleaned_data

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data["password"])  # Encripta la contraseña
        user.rol = 'cliente'  # Asignar rol automáticamente
        if commit:
            user.save()
        return user
    
#------------------------------------------------------------------------------------------------------
#------------------  CLASE PARA EL FORMULARIO DE LOGIN CLIENTE (login.html) ---------------------------
#------------------------------------------------------------------------------------------------------
class LoginForm(forms.Form):
    email = forms.EmailField(
        label="Correo Electrónico",
        max_length=254,
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'Ingrese su correo electrónico',
        }),
        error_messages={
            'invalid': "Introduce un correo electrónico válido.",
            'required': "El campo de correo es obligatorio.",
        },
    )
    password = forms.CharField(
        label="Contraseña",
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Ingrese su contraseña',
        }),
        min_length=8,
        error_messages={
            'required': "El campo de contraseña es obligatorio.",
            'min_length': "La contraseña debe tener al menos 8 caracteres.",
        },
    )

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if not email:
            raise ValidationError("El correo electrónico es obligatorio.")
        return email

    def clean_password(self):
        password = self.cleaned_data.get('password')
        if not password:
            raise ValidationError("La contraseña es obligatoria.")
        if len(password) < 8:
            raise ValidationError("La contraseña debe tener al menos 8 caracteres.")
        return password

    def clean(self):
        """
        Validación final para asegurarse de que el correo y la contraseña
        sean correctos. Delega la autenticación en la vista.
        """
        cleaned_data = super().clean()
        email = cleaned_data.get('email')
        password = cleaned_data.get('password')

        if email and password:
            user = authenticate(email=email, password=password)
            if not user:
                raise ValidationError("Credenciales incorrectas. Verifica tus datos.")
            elif user.rol != 'cliente':  # Validación adicional para clientes
                raise ValidationError("Solo los clientes pueden iniciar sesión aquí.")
        return cleaned_data

#------------------------------------------------------------------------------------------------------
#------------------  CLASE PARA FORMULARIO DE EDITAR PERFIL (editar_perfil.html) ----------------------
#------------------------------------------------------------------------------------------------------
class EditarPerfilForm(forms.ModelForm):
    telefono = forms.CharField(
        required=False,  # Opcional
        validators=[
            RegexValidator(
                regex=r'^\+?\d{7,15}$',
                message="El número de teléfono debe contener entre 7 y 15 dígitos, opcionalmente con un prefijo '+'."
            )
        ],
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Ingrese su teléfono',
        })
    )

    direccion = forms.CharField(
        required=False,  # Opcional
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Ingrese su dirección',
        }),
        max_length=255
    )

    class Meta:
        model = Usuario
        fields = ['nombre', 'email', 'telefono', 'direccion']
        widgets = {
            'nombre': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ingrese su nombre',
            }),
            'email': forms.EmailInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ingrese su correo electrónico',
            }),
        }

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if Usuario.objects.filter(email=email).exclude(pk=self.instance.pk).exists():
            raise ValidationError("Este correo electrónico ya está registrado por otro usuario.")
        return email

#------------------------------------------------------------------------------------------------------
#--------  CLASE PARA FORMULARIO DE CAMBIAR CONTRASEÑA (cambiar_contrasena.html) ----------------------
#------------------------------------------------------------------------------------------------------

class CustomPasswordChangeForm(PasswordChangeForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Agregar clases CSS a los campos
        self.fields['old_password'].widget.attrs.update({'class': 'form-control', 'placeholder': 'Ingrese su contraseña antigua'})
        self.fields['new_password1'].widget.attrs.update({'class': 'form-control', 'placeholder': 'Ingrese su nueva contraseña'})
        self.fields['new_password2'].widget.attrs.update({'class': 'form-control', 'placeholder': 'Confirme su nueva contraseña'})

    def clean_new_password2(self):
        password = self.cleaned_data.get('new_password1')
        confirm_password = self.cleaned_data.get('new_password2')

        if password and confirm_password and password != confirm_password:
            raise ValidationError("Las contraseñas no coinciden.")
        if len(password) < 8:
            raise ValidationError("La contraseña debe tener al menos 8 caracteres.")
        if not any(char.isdigit() for char in password):
            raise ValidationError("La contraseña debe contener al menos un número.")
        if not any(char.isalpha() for char in password):
            raise ValidationError("La contraseña debe contener al menos una letra.")

        return confirm_password

