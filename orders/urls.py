
from django.contrib import admin
from django.urls import path, include

from backend.views import initial_page, import_products, ExportProductsView
from backend import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', initial_page),
    path('api/', include('backend.urls')),
    path('export/products/', ExportProductsView.as_view(), name='export-products'),
    path('import/products/', import_products, name='import-products'),
    path('activate/<uidb64>/<token>/', views.activate, name='activate'),
    path('cart/', views.get_cart, name='get_cart'),
    path('cart/add/', views.add_to_cart, name='add_to_cart'),
    path('cart/item/<int:item_id>/update/', views.update_cart_item, name='update_cart_item'),
    path('cart/item/<int:item_id>/delete/', views.remove_from_cart, name='remove_from_cart'),
]

