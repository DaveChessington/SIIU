from django.contrib.auth import login, logout, authenticate, get_user_model
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.shortcuts import render, redirect
from django.urls import reverse_lazy
from django.views import View
from django.views.generic import ListView, CreateView, FormView

from inventory.models import Building
from .forms import UserLoginForm, UserRegWithRoleAndBuildingForm
from .models import User
import json

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

        buildings = list(Building.objects.values('id', 'name'))

        context['buildings'] = json.dumps(buildings)
        return context

class UserRegWithRoleAndBuildingView(UserManagementMixin, FormView):
    model = User
    form_class  = UserRegWithRoleAndBuildingForm
    template_name = 'new_user.html'
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
def logoutView(request):
    logout(request)
    return redirect('login')


@login_required
def profileView(request):
    if request.method == 'POST':
        pass

    return render(request, 'profile.html')
