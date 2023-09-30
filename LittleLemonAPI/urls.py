from django.urls import path, include
from . import views
from django.contrib.auth.models import User
#from rest_framework.authtoken.views import obtain_auth_token

urlpatterns = [
    path('menu-items', views.MenuItemView.as_view()),
    path('menu-items/<int:pk>', views.MenuItemView.single_item),
    path('category', views.CategoryView.as_view()),
    path('cart/menu-items', views.CartAddAPIView.as_view(), name = 'add_to_cart'),
    path('cart/menu-items/<int:pk>', views.CartView.cartitemview),
    path('orders', views.UserOrderListAPIView.as_view(), name = 'add_to_order'),
    path('orders/<int:pk>', views.UserOrderListAPIView.orderitem_view),
    path('', include('djoser.urls')),
    path('groups/managers/users', views.managers),
    path('groups/managers/users/<int:id>', views.managers),


]
