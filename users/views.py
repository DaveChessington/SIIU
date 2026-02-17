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
from .forms import UserLoginForm, UserRegWithRoleAndBuildingForm
from .models import User, Role
import json

#Import the date filter
from django.template.defaultfilters import date as date_filter

from django.views.decorators.http import require_POST
from django.shortcuts import get_object_or_404
from django.contrib import messages
from django.contrib.auth.forms import PasswordChangeForm


class LoginView(View):
    def get(self, request):
        form = UserLoginForm()
        return render(request, 'login.html', {'form': form})

    def post(self, request):
        form = UserLoginForm(request.POST)
        if form.is_valid():
            # get the cleaned data
            email = form.cleaned_data['email']
            password = form.cleaned_data['password']

            # Authenticate against the database
            user = authenticate(request, email=email, password=password)

            if user is not None:
                # User is authenticated
                login(request, user)
                return redirect('dashboard')
            else:
                form.add_error(None, 'Correo o contraseña inválidos')

        return render(request, 'login.html', {'form': form})


class UserManagementMixin(LoginRequiredMixin, PermissionRequiredMixin):
    permission_required = "users.can_manage_users"
    raise_exception = True


class UserListView(UserManagementMixin, ListView):
    model = User
    queryset = User.objects.select_related('building').all()
    template_name = "user_list.html"
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
            profile_picture = "default.png"

            if hasattr(user, 'profile') and user.profile.profile_picture:
                profile_picture = user.profile.profile_picture

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

        # user_list = [{
        #     'id': user.id,
        #     'email': user.email,
        #     'partial_name': user.get_partial_name,
        #     'profile_pic_url': static(f"avatars/{user.profile.profile_picture}.png") if user.profile else static(f"avatars/default.png"),
        #     'rol': 'Admin' if user.role == Role.ADMIN else 'Usuario',
        #     'is_active': user.is_active,
        #     'date_joined': date_filter(user.date_joined, "j F, Y P"),
        #     'last_login': timesince(user.last_login).split(',')[0] if user.last_login else "Nunca",
        #     'building': user.building.name if user.building else 'No establecido'
        # } for user in users_qs]

        context['users_json'] = json.dumps(user_list, cls=DjangoJSONEncoder)
        return context


class UserRegWithRoleAndBuildingView(UserManagementMixin, FormView):#display form and validate
    model = User #data saved on Users table
    form_class = UserRegWithRoleAndBuildingForm #contains the fields,layout adn validations
    template_name = 'new_user.html'
    success_url = reverse_lazy('user_list')

    def form_valid(self, form): #called when correct validation
        data = form.cleaned_data
        User.objects.create_user( #create the user
            email=data['email'],
            password=data['password'],
            role=data['role'],
            first_name=data['first_name'],
            last_name=data['last_name'],
            building=data['building'],
        )
        return super().form_valid(form)
    """"""
    def get_context_data(self, **kwargs):#data sent to the HTML template.
        context = super().get_context_data(**kwargs) #call parent's method before override 
        form = context['form'] #retrieve context dict and mod it
        
        context['field_layout'] = []

        for row in form.field_layout:
            fields = [form[field_name] for field_name in row]
            col_size = int(12 / len(fields))
            context['field_layout'].append({
                'fields': fields,
                'col': col_size
            })

        return context

    # def get(self, request):
    #     form = UserRegistrationWithRoleForm()
    #     return render(request, 'user_registration.html', {'form': form})
    #
    # def post(self, request):
    #     form = UserRegistrationWithRoleForm(request.POST)
    #     if form.is_valid():
    #         # get cleaned data
    #         name = form.cleaned_data['first_name']
    #         last_name = form.cleaned_data['last_name']
    #         email = form.cleaned_data['email']
    #         password = form.cleaned_data['password']
    #         rol = form.cleaned_data['role']
    #
    #         User.objects.create_user(name, last_name, email, password, rol)
    #
    #         return redirect('')
    #
    #     return render(request, 'new_user.html', {'form': form})


@login_required
@permission_required('users.can_manage_users', raise_exception=True)
@require_POST
def changeUserStatus(request, user_id):
    user = get_object_or_404(User, id=user_id)

    if request.user == user:
        messages.error(request, "No puedes cambiar el estado de tu propio usuario.")
        return redirect('user_list')
    
    user.is_active = not user.is_active
    user.save()

    status = "activado" if user.is_active else "desactivado"
    messages.success(request, f"El usuario {user.get_partial_name} ha sido {status} exitosamente.")
    return redirect('user_list')

@login_required
@permission_required('users.can_manage_users', raise_exception=True)
def changeUserPassword(request, user_id):
    user = get_object_or_404(User, id=user_id)
    form = PasswordChangeForm(user)
    if request.method == 'POST':
        pass
    
    return render(request, 'change_user_password.html', {'form': form, 'user': user})


@login_required
def logoutView(request):
    logout(request)
    return redirect('login')


@login_required
def profileView(request):
    if request.method == 'POST':
        pass

    return render(request, 'user_profile.html')
