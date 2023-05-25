import datetime
from datetime import datetime, timedelta
from django.contrib.auth import get_user_model
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import send_mail
from django.db import models
from django.db.models import F, ExpressionWrapper, Func
from djoser import signals, utils
from djoser.conf import settings
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.exceptions import NotFound
from rest_framework.pagination import LimitOffsetPagination
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.viewsets import GenericViewSet, ModelViewSet

from .permissions import Unsafe4AdminsOnly
from .serializers import CarSerializer, OrderSerializer, CustomerSerializer, DriverSerializer, CustomerInfoSerializer
from .models import Car, Order

User = get_user_model()


class CarViewSet(ModelViewSet):
    queryset = Car.objects.all()
    serializer_class = CarSerializer

    permission_classes = [Unsafe4AdminsOnly]
    pagination_class = LimitOffsetPagination


class OrderViewSet(ModelViewSet):
    queryset = Order.objects.all()
    serializer_class = OrderSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        is_curr = self.request.query_params.get('is_curr')
        is_past = self.request.query_params.get('is_past')
        if is_curr is not None and is_curr=="true":
            curr = datetime.now().timestamp()
            queryset = Order.objects.filter(owner=self.request.user)
            queryset_none = set()
            for item in queryset:
                if (item.start_date + timedelta(days=item.rental_days)).timestamp() > curr:
                    queryset_none.add(item)

            return queryset_none
        if is_past is not None and is_past=="true":
            curr = datetime.now().timestamp()
            queryset = Order.objects.filter(owner=self.request.user)
            queryset_none = set()
            for item in queryset:
                if (item.start_date + timedelta(days=item.rental_days)).timestamp() < curr:
                    queryset_none.add(item)

            return queryset_none

        return super(OrderViewSet, self).get_queryset()




class UserViewSet(ModelViewSet):
    queryset = User.objects.all()
    permission_classes = settings.PERMISSIONS.user
    token_generator = default_token_generator
    lookup_field = settings.USER_ID_FIELD

    def permission_denied(self, request, **kwargs):
        if (
                settings.HIDE_USERS
                and request.user.is_authenticated
                and self.action in ["update", "partial_update", "list", "retrieve"]
        ):
            raise NotFound()
        super().permission_denied(request, **kwargs)

    def get_queryset(self):
        user = self.request.user
        queryset = super().get_queryset()
        if settings.HIDE_USERS and self.action == "list" and not user.is_staff:
            queryset = queryset.filter(pk=user.pk)
        return queryset

    def get_instance(self):
        return self.request.user

    def perform_create(self, serializer, *args, **kwargs):
        user = serializer.save(*args, **kwargs)
        signals.user_registered.send(
            sender=self.__class__, user=user, request=self.request
        )

    def perform_update(self, serializer, *args, **kwargs):
        super().perform_update(serializer)
        user = serializer.instance
        signals.user_updated.send(
            sender=self.__class__, user=user, request=self.request
        )

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data)
        serializer.is_valid(raise_exception=True)

        if instance == request.user:
            utils.logout_user(self.request)
        self.perform_destroy(instance)
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(["get", "put", "patch", "delete"], detail=False)
    def me(self, request, *args, **kwargs):
        self.get_object = self.get_instance
        if request.method == "GET":
            return self.retrieve(request, *args, **kwargs)
        elif request.method == "PUT":
            return self.update(request, *args, **kwargs)
        elif request.method == "PATCH":
            return self.partial_update(request, *args, **kwargs)
        elif request.method == "DELETE":
            return self.destroy(request, *args, **kwargs)


class CustomerViewSet(UserViewSet):
    serializer_class = CustomerSerializer

    def get_permissions(self):
        if self.action == "create":
            self.permission_classes = settings.PERMISSIONS.user_create
        elif self.action == "destroy" or (
                self.action == "me" and self.request and self.request.method == "DELETE"
        ):
            self.permission_classes = settings.PERMISSIONS.user_delete
        return super().get_permissions()

    def get_serializer_class(self):
        if self.action == "create":
            return CustomerSerializer
        elif self.action == "destroy" or (
                self.action == "me" and self.request and self.request.method == "DELETE"
        ):
            return settings.SERIALIZERS.user_delete
        elif self.action == "me":
            return CustomerInfoSerializer

        return self.serializer_class


class DriverViewSet(UserViewSet):
    serializer_class = DriverSerializer

    def get_permissions(self):
        if self.action == "create":
            self.permission_classes = settings.PERMISSIONS.user_create
        elif self.action == "destroy" or (
                self.action == "me" and self.request and self.request.method == "DELETE"
        ):
            self.permission_classes = settings.PERMISSIONS.user_delete
        return super().get_permissions()

    def get_serializer_class(self):
        if self.action == "create":
            return DriverSerializer
        elif self.action == "destroy" or (
                self.action == "me" and self.request and self.request.method == "DELETE"
        ):
            return settings.SERIALIZERS.user_delete
        elif self.action == "me":
            return settings.SERIALIZERS.current_user

        return self.serializer_class


class SendEmailView(APIView):
    def post(self, request):
        sender = request.data.get("sender")
        message = request.data.get("message")
        if sender is not None and message is not None:
            send_mail("Обратная связь", f"Сообщение от: {sender}\nТекст сообщения: {message}",
                      "pmk.company2023@yandex.ru", ["pmk.company2023@yandex.ru"], fail_silently=False)
            return Response(status=status.HTTP_200_OK)

        return Response(status=status.HTTP_400_BAD_REQUEST)