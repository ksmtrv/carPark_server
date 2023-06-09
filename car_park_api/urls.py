from django.urls import include, path
from rest_framework import routers
from .views import CustomerViewSet, DriverViewSet, CarViewSet, OrderViewSet, SendEmailView, CurrentUserRoleView, \
    VerifySecretWord, SetNewPass

router = routers.SimpleRouter()
router.register('auth/users/customers', CustomerViewSet)
router.register('auth/users/drivers', DriverViewSet)
router.register('cars', CarViewSet)
router.register('orders', OrderViewSet)
router.register('currentrole', CurrentUserRoleView)

# Wire up our API using automatic URL routing.
# Additionally, we include login URLs for the browsable API.
urlpatterns = [
    path('', include(router.urls)),
    path('api-auth/', include('rest_framework.urls', namespace='rest_framework')),
    path('auth/', include('djoser.urls.jwt')),
    path('send_email/', SendEmailView.as_view()),
    path('verify_secret/', VerifySecretWord.as_view()),
    path('new_pass_by_tel/', SetNewPass.as_view())
]

urlpatterns += router.urls
