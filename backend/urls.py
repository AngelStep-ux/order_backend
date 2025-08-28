from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenRefreshView

from . import views
from .views import (
    CategoryViewSet,
    ProductViewSet,
    ShopViewSet,
    OrderViewSet,
    RegisterView,
    CustomTokenObtainPairView,
    get_products,
    import_products,
    ProductInfoListView,
    ContactListCreateView,
    ContactDestroyView,
    CreateOrderView,
    ConfirmOrderByLinkView,
    SendOrderConfirmationView,
    add_to_cart,
    ListOrdersView,
    UserOrdersPageView,
    OrderDetailAPIView
)

router = DefaultRouter()
router.register(r'categories', CategoryViewSet)
router.register(r'products', ProductViewSet)
router.register(r'shops', ShopViewSet)
router.register(r'orders', OrderViewSet, basename='order')

urlpatterns = [
    path('', include(router.urls)),
    path('register/', RegisterView.as_view(), name='register'),
    path('token/', CustomTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),

    path('products/list/', get_products, name='get_products'),
    path('import-products/', import_products, name='import_products'),

    path('product-info/', ProductInfoListView.as_view(), name='product_info_list'),

    path('contacts/', ContactListCreateView.as_view(), name='contacts_list_create'),
    path('contacts/<int:pk>/', ContactDestroyView.as_view(), name='contact_delete'),

    path('orders/', ListOrdersView.as_view(), name='list_orders'),
    path('my-orders/', UserOrdersPageView.as_view(), name='user_orders_page'),
    path('my-orders/<int:pk>/', OrderDetailAPIView.as_view(), name='order-details'),

    path('orders/create/', CreateOrderView.as_view(), name='create_order'),
    path('api/orders/<int:order_id>/send_confirmation/', SendOrderConfirmationView.as_view(), name='send_order_confirmation'),
    path('orders/<str:uidb64>/confirm/', ConfirmOrderByLinkView.as_view(), name='confirm_order'),
    path('cart/add/', add_to_cart, name='add_to_cart'),
    path('cart/', views.get_cart, name='get_cart'),
    path('cart/item/<int:item_id>/update/', views.update_cart_item, name='update_cart_item'),
    path('cart/item/<int:item_id>/delete/', views.remove_from_cart, name='remove_from_cart'),
]