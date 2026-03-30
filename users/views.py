from django.contrib.admindocs.utils import ROLES
from django.contrib.auth import login, logout, authenticate, get_user_model
from django.contrib.auth.decorators import login_required, permission_required
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.core.serializers.json import DjangoJSONEncoder
from django.shortcuts import render, redirect
from django.templatetags.static import static
from django.urls import reverse_lazy
from django.utils.timesince import timesince
from django.views import View
from django.views.generic import ListView, CreateView, FormView

from inventory.models import Building
from .forms import UserLoginForm, UserRegWithRoleAndBuildingForm, CustomPasswordChangeForm, UpdateUserForm
from .models import User, Role
import json

#Import the date filter
from django.template.defaultfilters import date as date_filter

from django.views.decorators.http import require_POST
from django.shortcuts import get_object_or_404
from django.contrib import messages
from django.utils.decorators import method_decorator
from django_ratelimit.decorators import ratelimit

@method_decorator(ratelimit(key='post:email', rate='5/m', block=False), name='post')
@method_decorator(ratelimit(key='post:ip', rate='5/m', block=False), name='post')
class LoginView(View):
    def get(self, request, form=None, is_limited=False):
        if form is None:
            form = UserLoginForm()
        return render(request, 'pages/auth/login.html', {'form': form, 'is_limited':is_limited})
    
    def post(self, request):
        # Check if reate limit was exceeded
        if getattr(request, 'limited', False):
            messages.error(request, "Has superado el límite de intentos permitidos. Inténtalo de nuevo en un minuto.")
            return self.get(request, is_limited=True)
        
        form = UserLoginForm(request.POST)
        if form.is_valid():
            # get the cleaned data
            email = form.cleaned_data['email']
            password = form.cleaned_data['password']

            # Looks for a user against the database according to the provided credentials
            user = authenticate(request, email=email, password=password)

            if user is not None:
                # If the user was found do:
                login(request, user)
                if user.password_must_change:
                    return redirect('change_own_password')
                return redirect('dashboard')
            else:
                # If the user was not found:
                form.add_error(None, 'Correo o contraseña inválidos')

        return self.get(request, form=form)
    
@login_required
def changeOwnPassword(request):
    user = request.user
    form = CustomPasswordChangeForm(user)
    if request.method == 'POST':
        form = CustomPasswordChangeForm(user, request.POST)
        if form.is_valid():
            form.save()
            # After changing the password, set password_must_change to False
            user.password_must_change = False
            user.save(update_fields=['password_must_change'])
            # Login the user out
            logout(request)
            # Letting the user know what had happened
            messages.success(request, "Tu contraseña ha sido cambiada exitosamente.")
            messages.info(request, "Inicia sesión con tu nueva contraseña.")
            #Redirecting the user to login page
            return redirect('login')
    return render(request, 'pages/auth/change_own_password.html', {'form': form})

@login_required
@permission_required('users.can_manage_users', raise_exception=True)
@require_POST
def changeUserPassword(request, user_id):
    user = get_object_or_404(User, pk=user_id)

    if user.is_admin:
        messages.error(request, "No puedes cambiar la contraseña de un administrador.")
    else:
        if( request.method == 'POST'):
            new_password = request.POST.get('new-password')

            if new_password :
                user.set_password(new_password)
                user.password_must_change = True
                user.save(update_fields=['password', 'password_must_change'])
                messages.success(request, f"La contraseña ha sido restablecida con exito para el usuario {user.get_partial_name}")
            else:
                messages.warning(request, "No se restableció ninguna contraseña. Inténtalo de nuevo.")

    return redirect('user_list')

@login_required
@permission_required('users.can_manage_users', raise_exception=True)
def updateUserView(request, user_id):
    user = get_object_or_404(User, pk=user_id)
    
    if user.is_admin:
        messages.warning(request, "No puedes modificar a un usuario administrador.")
        return redirect('user_list')

    if request.method == 'POST':
        form = UpdateUserForm(request.POST, instance=user)
        if form.is_valid():
            if form.has_changed():
                # Since the form inherits from ModelForm, 
                # there's no need to map each form field to the user's model ones. 
                form.save() 
                messages.success(request, f"El usuario {user.get_partial_name} ha sido actualizado con exito.")
            else:
                messages.info(request, "No se ha realizado ningún cambio.")
            
            return redirect('user_list')
    else:
        form = UpdateUserForm(instance=user)

    return render(request, 'pages/users/update_user.html', {
        'form': form,
        'target_user': user
    })

#
# TODO Update user profile view
#

class UserManagementMixin(LoginRequiredMixin, PermissionRequiredMixin):
    permission_required = "users.can_manage_users"
    raise_exception = True

class UserListView(UserManagementMixin, ListView):
    model = User
    queryset = User.objects.select_related('building').all()
    template_name = "pages/users/user_list.html"
    context_object_name = "users"
    ordering = ['-date_joined']

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Serialize Buildings
        buildings = list(Building.objects.values('id', 'name'))
        context['buildings'] = json.dumps(buildings)
        # Serialize Users

        users_qs = self.get_queryset()
        user_list = []

        for user in users_qs:

            profile_picture = ( 
                user.profile.profile_picture 
                if hasattr(user, 'profile') and user.profile.profile_picture
                else "default.png"
            )
                               

            user_data = {
                'id': user.id,
                'email': user.email,
                'name': user.get_partial_name,
                'profile_pic_url': static(f"avatars/{profile_picture}"),
                'role': 'Admin' if user.role == Role.ADMIN else 'Usuario',
                'is_active': user.is_active,
                'date_joined': date_filter(user.date_joined, "j F, Y"),
                'last_login': "Hace " + timesince(user.last_login).split(',')[0] if user.last_login else "Nunca",
                'building': user.building.name if user.building else 'No establecido'
            }
            user_list.append(user_data)

        context['users_json'] = user_list
        # context['users_json'] = json.dumps(user_list, cls=DjangoJSONEncoder)
        return context


class UserRegWithRoleAndBuildingView(UserManagementMixin, FormView):
    model = User
    form_class = UserRegWithRoleAndBuildingForm
    template_name = 'pages/users/new_user.html'
    success_url = reverse_lazy('user_list')

    def form_valid(self, form):
        data = form.cleaned_data
        User.objects.create_user(
            email=data['email'],
            password=data['password'],
            role=data['role'],
            first_name=data['first_name'],
            last_name=data['last_name'],
            building=data['building'],
        )
        return super().form_valid(form)

@login_required
@permission_required('users.can_manage_users', raise_exception=True)
@require_POST
def changeUserStatus(request, user_id):
    user = get_object_or_404(User, id=user_id)

    if request.user == user:
        messages.warning(request, "No puedes cambiar el estado de tu propio usuario.")
        return redirect('user_list')
    
    user.is_active = not user.is_active
    user.save()

    status = "activado" if user.is_active else "desactivado"
    messages.success(request, f"El usuario {user.get_partial_name} ha sido {status} exitosamente.")
    return redirect('user_list')

@login_required
@require_POST
def logoutView(request):
    logout(request)
    return redirect('login')

#
#TODO
#
@login_required
def profileView(request):
    if request.method == 'POST':
        pass

    return render(request, 'pages/users/user_profile.html')
