from datetime import datetime
import re
from djoser.serializers import UserCreateSerializer
from rest_framework import serializers
from django.utils import timezone

from .models import Car, Order, User


class CarSerializer(serializers.ModelSerializer):
    class Meta:
        model = Car
        fields = ('id',
                  'name',
                  'year_release',
                  'mileage',
                  'volume',
                  'power',
                  'box',
                  'engine_type',
                  'fuel',
                  'drive',
                  'overclocking',
                  'price',
                  'car_image')

    def validate(self, attrs):
        year_release = attrs.get('year_release')
        mileage = attrs.get('mileage')
        volume = attrs.get('volume')
        power = attrs.get('power')
        price = attrs.get('price')

        self.validate_year_release(year_release)
        self.validate_mileage(mileage)
        self.validate_volume(volume)
        self.validate_power(power)
        self.validate_price(price)

        return attrs

    def validate_year_release(self, value):
        current_year = timezone.now().year
        if value < 1950 or value > current_year:
            raise serializers.ValidationError(
                "Год выпуска автомобиля должен быть не меньше 1950 и не больше текущего года.")

    def validate_mileage(self, value):
        if value < 0:
            raise serializers.ValidationError("Пробег не может быть отрицательным.")

    def validate_volume(self, value):
        if value <= 0:
            raise serializers.ValidationError("Объем двигателя должен быть положительным числом.")

    def validate_power(self, value):
        if value <= 0:
            raise serializers.ValidationError("Мощность двигателя должна быть положительным числом.")

    def validate_price(self, value):
        if value <= 0:
            raise serializers.ValidationError("Цена должна быть больше 0.")


class OrderSerializer(serializers.ModelSerializer):
    class Meta:
        model = Order
        fields = ('id',
                  'owner',
                  'driver',
                  'car',
                  'first_name',
                  'last_name',
                  'patronymic',
                  'date_birth',
                  'phone_number',
                  'passport_number',
                  'passport_issued_by',
                  'passport_issue_date',
                  'registration_address',
                  'driver_license_number',
                  'delivery_type',
                  'delivery_address',
                  'pickup_address',
                  'start_date',
                  'rental_days',
                  'payment_method',
                  'is_paid',
                  'is_delivered')


class UserSerializer(UserCreateSerializer):
    password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ('phone_number',
                  'secret_word',
                  'password',
                  'first_name',
                  'last_name',
                  'patronymic',
                  )

    def validate(self, attrs):
        return attrs

    def inner_create(self, validated_data, is_driver=False):
        user = User.objects.create(phone_number=validated_data['phone_number'],
                                   secret_word=validated_data['secret_word'],
                                   first_name=validated_data['first_name'],
                                   last_name=validated_data['last_name'],
                                   patronymic=validated_data['patronymic'],
                                   is_driver=is_driver)
        user.set_password(validated_data['password'])
        user.save()

        return user


class CustomerSerializer(UserSerializer):
    def create(self, validated_data):
        return super(CustomerSerializer, self).inner_create(validated_data)


class DriverSerializer(UserSerializer):
    def create(self, validated_data):
        return super(DriverSerializer, self).inner_create(validated_data, True)


class CustomerInfoSerializer(UserSerializer):
    class Meta:
        model = User
        fields = ('id',
                  'email',
                  'first_name',
                  'last_name',
                  'patronymic',
                  )
