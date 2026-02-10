import email

from django import forms
from django.core.exceptions import ValidationError

from users.models import User
from utilities.generics import format_masculine_feminine


class UserLoginForm(forms.Form):
    email = forms.EmailField(label='Email')
    password = forms.CharField(widget=forms.PasswordInput, label='Contraseña')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        #Adding bootstrap class to all fields
        for field_name, field in self.fields.items():
            field.widget.attrs['class'] = 'form-control'
            field.required = True
            field.error_messages['required'] = f"Por favor ingresa tu {field.label.lower()}"

class UserRegistrationForm(forms.ModelForm):
    confirm_password = forms.CharField(widget=forms.PasswordInput, label='Confirmar contraseña', error_messages={'required': 'Por favor confirma la contraseña del nuevo usuario'})

    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email', 'password', 'confirm_password']
        labels = {'first_name': 'Nombre', 'last_name': 'Apellidos', 'email': 'Email', 'password': 'Contraseña'}
        widgets = {'password': forms.PasswordInput()}
        error_messages = {
            'email': {'unique': 'Este email ya fue asociado a otro usuario',
                      'invalid': 'El formato del email no es correcto'},
        }
    def __init__(self, *args, **kwargs):
        super(UserRegistrationForm, self).__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            field.required = True
            field.widget.attrs['class'] = 'form-control'

            if field_name == 'confirm_password':
                continue
            determiner = format_masculine_feminine(field.label)
            field.error_messages['required'] = f"Por favor ingresa {determiner} {field.label.lower()} del nuevo usuario"

    def clean(self):
        cleaned_data = super().clean()
        # # Validating the email non existence
        # email = cleaned_data.get('email')
        # if email and User.objects.filter(email=email).exists():
        #     raise ValidationError("Este email ya está relacionado con un usuario")

        password = cleaned_data.get("password")
        confirm_password = cleaned_data.get("confirm_password")

        if password and confirm_password and password != confirm_password:
            raise ValidationError("Las contraseñas no coinciden.")

        return cleaned_data

class UserRegWithRoleAndBuildingForm(UserRegistrationForm):
    class Meta(UserRegistrationForm.Meta):
        fields = UserRegistrationForm.Meta.fields + ['role', 'building']
        labels = {**UserRegistrationForm.Meta.labels, 'role': 'Rol', 'building': 'Plantel'}
        
        widgets = {
            **UserRegistrationForm.Meta.widgets,
            'role': forms.Select(attrs={'class': 'form-control'}),
            'building': forms.Select(attrs={'class': 'form-control'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        #setting the building field as not required
        self.fields['building'].required = False




