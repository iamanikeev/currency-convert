from django.conf.urls import url, include
from api import views
from rest_framework.routers import DefaultRouter

router = DefaultRouter()
router.register(r'currency', views.CurrencyViewSet)
router.register(r'rate', views.RateViewSet)

# The API URLs are now determined automatically by the router.
# Additionally, we include the login URLs for the browsable API.
urlpatterns = [
    url(r'^', include(router.urls)),
    url(r'^currency/convert/(?P<base>.+)/(?P<target>.+)/(?P<amount>.+)/&?', views.ConvertCurrency.as_view(),
        name='currency-convert')
]
