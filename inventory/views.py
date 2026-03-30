from django.contrib.auth.decorators import login_required, permission_required
from django.db import transaction

from inventory.forms import BuildingForm, UserFormSet
from inventory.models import Request, Building
from django.shortcuts import render, get_object_or_404, redirect

from users.models import User


@login_required
def dashboard(request):
    return render(request, 'pages/dashboard/dashboard.html')


@login_required
@permission_required('inventory.global_view_buildings', raise_exception=True)
def building_list_view(request):
    buildings = Building.objects.all().order_by('name')
    return render(request, "pages/buildings/buildings.html", {'buildings': buildings})


@login_required
@permission_required('inventory.add_building', raise_exception=True)
def manage_building_users(request):
    if request.method == 'POST':
        building_form = BuildingForm(request.POST)
        user_formset = UserFormSet(request.POST)
        if building_form.is_valid() and user_formset.is_valid():
            with transaction.atomic():
                building = building_form.save()
                for user_form in user_formset:
                    if user_form.cleaned_data:
                        User.objects.create_user(
                            email=user_form.cleaned_data['email'],
                            password=user_form.cleaned_data['password'],
                            first_name=user_form.cleaned_data['first_name'],
                            last_name=user_form.cleaned_data['last_name'],
                            building=building
                        )
            return redirect('buildings')
    else:
        building_form = BuildingForm()
        user_formset = UserFormSet()

    return render(request, 'pages/buildings/new_building.html', {'form': building_form, 'formset': user_formset})

# class PlantelCreatewithUserView(LoginRequiredMixin, CreateView):
#     model = Plantel
#     form_class = PlantelForm
#     template_name = 'new_building.html'
#     success_url = reverse_lazy('planteles')
#

#     def get_context_data(self, **kwargs):
#         data = super().get_context_data(**kwargs)
#         if self.request.POST:
#             data['formset'] = UserFormSet(self.request.POST)
#         else:
#             data['formset'] = UserFormSet()
#         return data
#
#     def form_valid(self, form):
#         context = self.get_context_data()
#         formset = context['formset']
#
#         with transaction.atomic():
#             self.object = form.save()
#
#             if formset.is_valid():
#                 formset.instance = self.object
#                 formset.save()
#             else:
#                 return self.form_invalid(form)
#
#         return super().form_valid(form)


# def dashboard(request):
#     if request.user.role == Role.ADMIN:
#         pedidos = Pedido.objects.all()
#     else:
#         pedidos = Pedido.objects.filter(usuario = request.user).order_by('-fecha')
#
#     return render(request, 'dashboard.html', {'pedidos':pedidos})
#
# def aprobar_pedido(request, pk):
#     if request.method == 'POST':
#         pedido = get_object_or_404(Pedido, pk=pk)
#         try:
#             pedido.estado = Pedido.Status.APROBADO
#             pedido.save()
#             messages.success(request, "Inventario actualizado y pedido aprobado.")
#         except ValueError as e:
#             messages.error(request, str(e))
#     return redirect('dashboard')
#
# def rechazar_pedido(request, pk):
#     pedido = get_object_or_404(Pedido, pk=pk)
#     razon = request.POST.get('comentario_admin')
#
#     if not razon:
#         messages.error(request, "Debe explicar por qué está rechazando el pedido.")
#     else:
#         pedido.estado = Pedido.Status.RECHAZADO
#         pedido.comentario_admin = razon
#         pedido.save()
#         messages.warning(request, "Pedido rechazado.")
#    return redirect('dashboard')
