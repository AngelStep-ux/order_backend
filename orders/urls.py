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

]

