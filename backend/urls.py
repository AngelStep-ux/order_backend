from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    CategoryViewSet,
    ProductViewSet,
    ShopViewSet,
    OrderViewSet,
    RegisterView,
    CustomTokenObtainPairView,
    initial_page,
    get_products,
    import_products,
    ProductInfoListView,
    ContactListCreateView,
    ContactDestroyView,
    UserOrdersListView,
    CreateOrderView,
    ConfirmOrderView,
    UserOrderListView,
    SendOrderConfirmationView
)

router = DefaultRouter()
router.register(r'categories', CategoryViewSet)
router.register(r'products', ProductViewSet)
router.register(r'shops', ShopViewSet)
router.register(r'orders', OrderViewSet, basename='order')
router.register(r'order_items', OrderViewSet, basename='order-item')

urlpatterns = [
    path('', initial_page, name='initial_page'),
    path('api/', include(router.urls)),
    path('register/', RegisterView.as_view(), name='register'),
    path('token/', CustomTokenObtainPairView.as_view(), name='token_obtain_pair'),

    path('products/list/', get_products, name='get_products'),
    path('import-products/', import_products, name='import_products'),

    path('product-info/', ProductInfoListView.as_view(), name='product_info_list'),

    path('contacts/', ContactListCreateView.as_view(), name='contacts_list_create'),
    path('contacts/<int:pk>/', ContactDestroyView.as_view(), name='contact_delete'),

    path('my-orders/', UserOrdersListView.as_view(), name='user_orders'),

    path('create-order/', CreateOrderView.as_view(), name='create_order'),
    path('api/orders/<int:order_id>/send_confirmation/', SendOrderConfirmationView.as_view(), name='send_order_confirmation'),
    path('confirm_order/<str:uidb64>/', ConfirmOrderView.as_view(), name='confirm_order'),
]