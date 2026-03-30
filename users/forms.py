import email

from django import forms
from django.core.exceptions import ValidationError

from users.models import User
from utilities.generics import format_masculine_feminine

from django.contrib.auth.forms import PasswordChangeForm

from utilities.error_messages import FORM_ERRORS, AUTH_ERRORS

class UserLoginForm(forms.Form):
    email = forms.EmailField(label='Email')
    password = forms.CharField(widget=forms.PasswordInput, 
                               label='Contraseña')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        #Adding bootstrap class to all fields

        for field_name, field in self.fields.items():
            field.widget.attrs['class'] = 'form-control'
            field.required = True
            field.error_messages['required'] = FORM_ERRORS['required'].format(field=field.label.lower())
            # field.error_messages['required'] = f"Por favor ingresa tu {field.label.lower()}"

class UserRegistrationForm(forms.ModelForm):
    confirm_password = forms.CharField(label='Confirmar contraseña',
                                       widget=forms.PasswordInput(),
                                       error_messages={'required': FORM_ERRORS['password_confirmation_not_provided']})

    
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email', 'password', 'confirm_password']
        labels = {'first_name': 'Nombre', 'last_name': 'Apellidos', 'email': 'Email', 'password': 'Contraseña'}
        widgets = {'password': forms.PasswordInput()}
        error_messages = {
            'email': {
                'unique': AUTH_ERRORS['user_exists'],
                'invalid': AUTH_ERRORS['invalid_m'].format(field='correo')
            },
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            field.required = True
            field.widget.attrs['class'] = 'form-control'

            if field_name != 'confirm_password':
                determiner = format_masculine_feminine(field.label)
                field.error_messages['required'] = FORM_ERRORS['field_not_provided_for_user_registration'].format(
                    determiner=determiner, 
                    field=field.label.lower())
          

    def clean(self):
        cleaned_data = super().clean()

        password = cleaned_data.get("password")
        confirm_password = cleaned_data.get("confirm_password")

        if password and confirm_password and password != confirm_password:
            raise ValidationError(FORM_ERRORS['passwords_mismatch'])

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
        self.fields['building'].required = False

class UpdateUserForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'role', 'building']
        labels = {'first_name': 'Nombre', 'last_name':'Apellidos', 'role': 'Rol', 'building':  'Plantel'}

        widgets = {
            'role': forms.Select(),
            'building': forms.Select()
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        for field_name, field in  self.fields.items():
            field.widget.attrs['class'] = 'form-control'
            label = field.label
            if label != 'Plantel':
                field.required = True
                determiner = format_masculine_feminine(label)
                field.error_messages['required'] = FORM_ERRORS['field_not_provided_for_user_update'].format(
                    determiner=determiner, field=label.lower())
            
class CustomPasswordChangeForm(PasswordChangeForm):
    error_messages = {**PasswordChangeForm.error_messages, 
                      'password_mismatch': FORM_ERRORS['passwords_mismatch'],
                      'password_incorrect': FORM_ERRORS['incorrect_old_password']}
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['old_password'].label = "Contraseña anterior"
        self.fields['new_password1'].label = "Nueva contraseña"
        self.fields['new_password2'].label = "Confirmar nueva contraseña"

        for field_name, field in self.fields.items():
            field.widget.attrs['class'] = 'form-control'

# class ChangeUserPasswordForm(forms.Form):
#     new_password = forms.CharField(label='Contraseña', widget=forms.PasswordInput , required=True)
#     confirm_new_password = forms.CharField(label='Confirmar contraseña', widget=forms.PasswordInput, required=True)
    
#     def __init__(self, *args, **kwargs):
#         super().__init__(*args, **kwargs)
        
#         self.fields['new_password'].error_messages['required'] = FORM_ERRORS['password_not_provided_for_user_update']
#         self.fields['confirm_new_password'].error_messages['required'] = FORM_ERRORS['password_confirmation_not_provided']

#         for field_name, field in self.fields.items():
#             field.widget.attrs['class'] = 'form-control'
    
#     def clean(self):
#         cleaned_data = super().clean()
#         password = cleaned_data.get('new_password')
#         confirmed_password = cleaned_data.get('confirm_new_password')

#         if password and confirmed_password and password != confirmed_password:
#             raise ValidationError(FORM_ERRORS['passwords_mismatch'])
        
#         return  cleaned_data
