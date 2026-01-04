from django.db import models, transaction
from simple_history.models import HistoricalRecords


# Create your models here.
class Building(models.Model):
    name = models.CharField(max_length=100, unique=True)

    class Meta:
        permissions = [
            ("global_view_buildings", "Can view all the buildings"),
        ]

    def __str__(self):
        return self.name

class Department(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField()
    building = models.ForeignKey(Building, on_delete=models.PROTECT)

    class Meta:
        unique_together = ('name', 'building')

    def __str__(self):
        return f"{self.name} - {self.building.name}"

class Product(models.Model):
    name = models.CharField(max_length=100,  db_index=True)
    description = models.TextField()
    model = models.CharField(max_length=100)
    quantity = models.PositiveIntegerField()
    serial_number = models.CharField(max_length=100)

    department = models.ForeignKey(Department, on_delete=models.PROTECT, null=True, blank=True)

    history = HistoricalRecords()

   #class Meta:
        #unique_together = ('serial_number', 'department')
        ##indexes = [models.Index(fields=['no_serie', 'departamento'], name='producto_idx')]
    # class Meta:
    #     permissions = [
    #         ("can_manage_products", "Can manage products of their own building (view, create, update, delete)"),
    #     ]


    def __str__(self):
        return self.name

class Request(models.Model):
    class Status(models.TextChoices):
        PENDING = 'PENDING', 'Pending'
        APPROVED = 'APPROVED', 'Approved'
        REJECTED = 'REJECTED', 'Rejected'
        COMPLETED = 'COMPLETED', 'Completed'

    date =  models.DateTimeField(auto_now_add=True)
    description = models.TextField()
    user = models.ForeignKey('users.User', on_delete=models.PROTECT)
    status = models.CharField(max_length=50, choices=Status.choices, default=Status.PENDING, db_index=True)
    admin_note = models.TextField(null=True, blank=True)

    history = HistoricalRecords()

    class Meta:
        permissions = [
            ("global_view_requests", "Can view all the requests"),
            ("global_change_requests", "Can change all the requests"),
            ("global_delete_requests", "Can delete all the requests"),
        ]

    def save(self, *args, **kwargs):
        #check if this is an update and if status is changing to APROBADO
        if self.pk:
            old_status = Request.objects.only('status').get(pk = self.pk).estado
            #1. Block moving backward from APPROVED
            if old_status == self.Status.APPROVED and self.status not in [self.Status.COMPLETED, self.Status.APPROVED]:
                raise ValueError("No se puede revertir un pedido ya aprobado.")

            #2. Block changes once rejected or completed
            if old_status in [self.Status.COMPLETED, self.Status.REJECTED] and self.status != old_status:
                raise ValueError(f"No se puede revertir el estado de este pedido.")

            #3. Stock deduction (Moving to APPROVED)
            if old_status != self.Status.APPROVED and self.status == self.Status.APPROVED:
                with transaction.atomic():
                    for detail in self.details.all():
                        product = detail.producto
                        if product.cantidad >= detail.cantidad:
                            product.cantidad -= detail.cantidad
                            product.save()
                        else:
                            raise ValueError(f"No hay suficiente stock de {product.name} - {product.modelo}")
        super().save(*args, **kwargs)


class Request_Detail(models.Model):
    request = models.ForeignKey(Request, on_delete=models.CASCADE, related_name='details')
    product = models.ForeignKey(Product, on_delete=models.PROTECT)
    quantity = models.PositiveIntegerField()


# class Pedido(models.Model):
#     fecha = models.DateTimeField(auto_now_add=True)
#     descripcion = models.TextField()
#     plantel = models.ForeignKey(Plantel, on_delete=models.CASCADE)
#
# class Detalle_Pedido(models.Model):
#     pedido = models.ForeignKey(Pedido, on_delete=models.CASCADE)
#     producto = models.ForeignKey(Producto, on_delete=models.SET_NULL)
#     cantidad = models.IntegerField()

# class Registro(models.Model):
#     fecha_registro = models.DateTimeField(auto_now_add=True)
#     tipo = models.CharField(max_length=100)
#     nota = models.TextField()
#
#     departamento = models.ForeignKey(Departamento, on_delete=models.CASCADE)
#     plantel = models.ForeignKey(Plantel, on_delete=models.CASCADE)
#     usuario = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL)

# class Registro_Producto(models.Model):
#     registro = models.ForeignKey(Registro, on_delete=models.CASCADE)
#     producto = models.ForeignKey(Producto, on_delete=models.)


