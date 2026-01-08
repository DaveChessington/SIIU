from django import forms
from django.core.exceptions import ValidationError
from django.forms import inlineformset_factory

from inventory.models import Building
from users.forms import UserRegistrationForm
from users.models import User

class BuildingForm(forms.ModelForm):
    image_file = forms.ImageField(required=False)
    class Meta:
        model = Building
        fields = ['name', 'image_file']

UserFormSet = inlineformset_factory(
    Building,
    User,
    form=UserRegistrationForm,
    extra=0,
    can_delete=False,
)
