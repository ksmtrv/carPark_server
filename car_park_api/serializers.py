from rest_framework import serializers

from .models import Car, Order


class CarSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Car
        fields = ('name', 'price')#TODO: расширить


class OrderSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Order
        fields = ('owner', 'car')#TODO: расширить


class UserSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Order
        fields = ('first_name', 'last_name')#TODO: расширить