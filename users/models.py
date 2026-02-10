from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.db import models
from django.utils import timezone


# Create your models here.
class Role(models.TextChoices):
    ADMIN = "ADMIN", 'Admin'
    USER = "USER", 'User'


class UserManager(BaseUserManager):
    def create_superuser(self, email, password, **extra_fields):
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_staff', True)
        return self.create_user(email, password, Role.ADMIN, **extra_fields)

    def create_user(self, email, password, role=Role.USER, **extra_fields):
        if not email:
            raise ValueError('An email must be set')
        if not password:
            raise ValueError('A password must be set')

        required_fields = ['first_name', 'last_name']

        for field in required_fields:
            if not extra_fields.get(field):
                raise ValueError(f'Field {field.replace("_", " ")} is required')

        email = self.normalize_email(email)
        user = self.model(email=email, role=role, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)

        #adding the user to a group with permissions
        groups = {
            Role.ADMIN: 'Admin_group',
            Role.USER: 'User_group',
        }
        group_name = groups.get(user.role)
        if group_name:
            from django.contrib.auth.models import Group # Imported here to avoid circular issues
            group, _ = Group.objects.get_or_create(name=group_name)
            user.groups.add(group)

        return user


class ActiveUserManager(BaseUserManager):
    def get_queryset(self):
        # only return users who are actually active
        return super().get_queryset().filter(is_active=True)


class User(AbstractUser):
    username = None
    email = models.EmailField(unique=True)
    role = models.CharField(max_length=50, choices=Role.choices, default=Role.USER)
    is_active = models.BooleanField(default=True)
    deleted_at = models.DateTimeField(blank=True, null=True)
    #
    password_must_change = models.BooleanField(default=True)

    class Meta:
        permissions = [
            ("can_manage_users", "Can manage users (view, create, update, delete)"),
        ]

    def soft_delete(self):
        self.is_active = False
        self.deleted_at = timezone.now()
        self.save(update_fields=['is_active', 'deleted_at'])

    building = models.ForeignKey(
        'inventory.Building',
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )

    objects = UserManager()  # for creating users/auth
    active_objects = ActiveUserManager()  # for listing at the dashboard

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['first_name', 'last_name']

    def is_admin(self):
        return self.role == Role.ADMIN

    def is_regular_user(self):
        return self.role == Role.USER

    def __str__(self):
        return self.email

    @property
    def get_partial_name(self):
        complements = ['de', 'la', 'del', 'en', 'con', 'por', 'a', 'ma', 'los', 'las', 'd', 'lo', 'los', 'y', 'i',
                       'san', 'santo', 'santa', 'vila', 'villa']

        def find_real_name(name, real_name):
            # BASE CASE: If we ran out of words, return what we have
            if not name:
                return ' '.join(real_name)
            if name[0].lower() in complements:
                return find_real_name(name[1:], real_name + [name[0]])
            else:
                return ' '.join(real_name + [name[0]])

        first_name = find_real_name(self.first_name.strip().split(), []) if self.first_name.strip() else ''
        last_name = find_real_name(self.last_name.strip().split(), []) if self.last_name.strip() else ''

        return f'{first_name} {last_name}'

    def get_full_name(self):
        return '{} {}'.format(self.first_name, self.last_name)


class Profile_Picture(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    # profile_picture =   models.ImageField(
    #     upload_to = 'profile_pictures/',
    #     default='profile_pictures/default.jpg',
    # )
    profile_picture = models.CharField(max_length=20,
                                       choices=[
                                           ('1', 'Avatar 1'),
                                           ('2', 'Avatar 2'),
                                           ('3', 'Avatar 3'),
                                           ('4', 'Avatar 4'),
                                           ('5', 'Avatar 5'),
                                           ('6', 'Avatar 6'),
                                           ('7', 'Avatar 7'),
                                           ('8', 'Avatar 8'),
                                           ('9', 'Avatar 9'),
                                           ('10', 'Avatar 10'),
                                           ('default', 'Default'),
                                       ],
                                       default='default'
                                       )
    updated_at = models.DateTimeField(auto_now=True)
