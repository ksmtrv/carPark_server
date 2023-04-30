from djoser.serializers import UserCreateSerializer
from rest_framework import serializers

from .models import Car, Order, User


class CarSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Car
        fields = ('name', 'price')  # TODO: расширить


class OrderSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Order
        fields = ('owner', 'car')  # TODO: расширить


# class UserSerializer(serializers.HyperlinkedModelSerializer):
#     class Meta:
#         model = Order
#         fields = ('first_name', 'last_name')#TODO: расширить

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
        # TODO: validate fields

        return user


class CustomerSerializer(UserSerializer):
    def create(self, validated_data):
        return super(CustomerSerializer, self).inner_create(validated_data)


class DriverSerializer(UserSerializer):
    def create(self, validated_data):
        return super(DriverSerializer, self).inner_create(validated_data, True)
