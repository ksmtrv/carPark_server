import os

from django.core.validators import FileExtensionValidator
from django.db import models
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin, BaseUserManager
from phonenumber_field.modelfields import PhoneNumberField
from django.utils.translation import gettext_lazy as _
from django.contrib import auth
from django.contrib.auth.hashers import make_password
import django.utils.timezone
from datetime import datetime
from django.utils import formats
from pytils.translit import slugify


def transliterate_filename(filename):
    name, ext = os.path.splitext(filename)
    name = slugify(name)
    return f'{name}{ext}'


class Car(models.Model):
    name = models.CharField(_('Название'), max_length=100, blank=False, null=False, unique=True)
    year_release = models.IntegerField(_('Год выпуска'), blank=False, null=True)
    mileage = models.IntegerField(_('Пробег'), blank=False, null=True)
    volume = models.FloatField(_('Объем'), max_length=10, blank=False, null=True)
    power = models.IntegerField(_('Мощность'), blank=False, null=True)
    box_choices = [
        ('Механика', 'Механика'),
        ('Автомат', 'Автомат'),
        ('Робот', 'Робот'),
        ('Вариантная', 'Вариантная'),
    ]
    box = models.CharField(_('Коробка'), max_length=11, choices=box_choices, blank=False, null=True)
    engine_choisec = [
        ('Оппозитный', 'Оппозитный'),
        ('Рядный', 'Рядный'),
        ('V-типа', 'V-типа'),
        ('Квазитурбинный', 'Квазитурбинный'),
        ('Роторный', 'Роторный')
    ]
    engine_type = models.CharField(_('Двигатель'), max_length=14, choices=engine_choisec, blank=False, null=True)
    fuel = models.CharField(_('Топливо'), max_length=10, blank=False, null=True)
    drive_choices = [
        ('Задний', 'Задний'),
        ('Передний', 'Передний'),
        ('Полный', 'Полный'),
    ]
    drive = models.CharField(_('Привод'), max_length=8, choices=drive_choices, blank=False, null=True)
    overclocking = models.FloatField(_('Разгон'), max_length=10, blank=False, null=True)
    price = models.PositiveIntegerField(_('Стоимость'), blank=False, null=True)

    def get_image_path(self, filename):
        print("filename", filename)
        path = f'images/{transliterate_filename(filename)}'
        return path

    car_image = models.ImageField(_('Фотография машины'), upload_to=get_image_path, validators=[
        FileExtensionValidator(['png', 'jpg', 'gif'])], blank=True, null=True)

    def __str__(self):
        return str(self.name)


class Order(models.Model):
    owner = models.ForeignKey("User", verbose_name='Заказчик', on_delete=models.CASCADE, related_name='user_orders',
                              blank=False, null=False)
    driver = models.ForeignKey("User", verbose_name='Курьер', on_delete=models.DO_NOTHING, related_name='driver_orders',
                               blank=True, null=True)
    car = models.ForeignKey("Car", verbose_name='Машина', on_delete=models.DO_NOTHING, related_name='car_orders',
                            blank=False, null=False)
    first_name = models.CharField(_('Имя'), max_length=150, blank=False, null=True)
    last_name = models.CharField(_('Фамилия'), max_length=150, blank=False, null=True)
    patronymic = models.CharField(_('Отчество'), max_length=150, blank=False, null=True)
    date_birth = models.DateField(_('Дата рождения'), blank=False, null=True)
    phone_number = models.CharField(_('Номер телефона'), max_length=20, blank=False, null=True)
    passport_number = models.CharField(_('Серия и номер'), max_length=20, blank=False, null=True)
    passport_issued_by = models.CharField(_('Кем выдан'), max_length=200, blank=False, null=True)
    passport_issue_date = models.DateField(_('Дата выдачи'), blank=False, null=True)
    registration_address = models.CharField(_('Адрес регистрации'), max_length=200, blank=False, null=True)
    driver_license_number = models.CharField(_('Серия и номер ВУ'), max_length=20, blank=False, null=True)
    delivery_choices = [
        ('Доставка', 'Доставка'),
        ('Самовывоз', 'Самовывоз')
    ]
    delivery_type = models.CharField(_('Тип доставки'), max_length=9, choices=delivery_choices, blank=False, null=True)
    delivery_address = models.CharField(_('Адрес доставки'), max_length=100, blank=True, null=True,
                                        default='Университетская площадь, 1')
    pickup_address = models.CharField(_('Самовывоз'), max_length=100, blank=True, null=True)
    start_date = models.DateTimeField(_('Дата и время начала аренды'), blank=False, null=True)
    rental_days = models.PositiveIntegerField(_('Количество дней аренды'), blank=False, null=True)
    payment_choices = (
        ('QR-код', 'QR-код'),
        ('Наличные', 'Наличные')
    )
    payment_method = models.CharField(_('Способ оплаты'), max_length=8, choices=payment_choices, blank=False, null=True)
    is_paid = models.BooleanField(
        _('paid status'),
        default=False,
        help_text=_('Indicates whether this order has been paid for or not.'),
    )
    is_delivered = models.BooleanField(
        _('delivered status'),
        default=False,
        help_text=_('Indicates whether the customer has received this order or not.'),
    )

    def get_start_date(self):
        date = formats.date_format(self.start_date, format='DATETIME_FORMAT', use_l10n=True)
        return _(date)

    def __str__(self):
        return f"Заказчик {self.owner.get_fullname()} {self.car} {self.get_start_date()}"


class UserManager(BaseUserManager):
    use_in_migrations = True

    def _create_user(self, phone_number, secret_word, password, **extra_fields):
        if not phone_number:
            raise ValueError('The given phone_number must be set')

        user = self.model(phone_number=phone_number, secret_word=secret_word, **extra_fields)
        user.password = make_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, phone_number, secret_word=None, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', False)
        extra_fields.setdefault('is_superuser', False)
        return self._create_user(phone_number, secret_word, password, **extra_fields)

    def create_superuser(self, phone_number, secret_word=None, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')

        return self._create_user(phone_number, secret_word, password, **extra_fields)

    def with_perm(self, perm, is_active=True, include_superusers=True, backend=None, obj=None):
        if backend is None:
            backends = auth._get_backends(return_tuples=True)
            if len(backends) == 1:
                backend, _ = backends[0]
            else:
                raise ValueError(
                    'You have multiple authentication backends configured and '
                    'therefore must provide the `backend` argument.'
                )
        elif not isinstance(backend, str):
            raise TypeError(
                'backend must be a dotted import path string (got %r).'
                % backend
            )
        else:
            backend = auth.load_backend(backend)
        if hasattr(backend, 'with_perm'):
            return backend.with_perm(
                perm,
                is_active=is_active,
                include_superusers=include_superusers,
                obj=obj,
            )
        return self.none()


class User(AbstractBaseUser, PermissionsMixin):
    phone_number = PhoneNumberField(_('Номер телефона'), null=False, blank=False, unique=True)
    email = models.EmailField(_('Email'), null=True, blank=True, unique=False)
    secret_word = models.CharField(_('Секретное слово'), max_length=150, blank=False, null=False, unique=False)
    is_driver = models.BooleanField(
        _('driver status'),
        default=False,
        help_text=_('.'),
    )
    is_staff = models.BooleanField(
        _('staff status'),
        default=False,
        help_text=_('Designates whether the user can log into this admin site.'),
    )
    is_active = models.BooleanField(
        _('active'),
        default=True,
        help_text=_(
            'Designates whether this user should be treated as active. '
            'Unselect this instead of deleting accounts.'
        ),
    )

    first_name = models.CharField(_('Имя'), max_length=150, blank=True)
    last_name = models.CharField(_('Фамилия'), max_length=150, blank=True)
    patronymic = models.CharField(_('Отчество'), max_length=150, blank=True)

    EMAIL_FIELD = 'email'
    USERNAME_FIELD = 'phone_number'
    REQUIRED_FIELDS = ['secret_word']

    objects = UserManager()

    def get_fullname(self):
        return f"{self.last_name} {self.first_name[0]}. {self.patronymic[0]}. "

    def __str__(self):
        return str(self.phone_number)
