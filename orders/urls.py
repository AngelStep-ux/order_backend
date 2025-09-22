from django.contrib import admin
from django.urls import path, include
from backend.views import CrashTestView

from backend.views import initial_page, import_products, ExportProductsView, activate
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', initial_page),

    # API пути
    path('api/', include('backend.urls')),  # Ваши viewset / API в backend.urls

    # Экспорт/импорт, если они относятся к API — полезно их сюда включить
    path('api/export/products/', ExportProductsView.as_view(), name='export-products'),
    path('api/import/products/', import_products, name='import-products'),

    # Активация вне API
    path('activate/<uidb64>/<token>/', activate, name='activate'),

    # OpenAPI схема и документация
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    path('api/docs/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
    path('accounts/', include('allauth.urls')),  # allauth
    path('api/auth/', include('dj_rest_auth.urls')),  # dj-rest-auth базовые
    path('api/auth/registration/', include('dj_rest_auth.registration.urls')),  # регистрация
    path('api/auth/social/', include('allauth.socialaccount.urls')),  # social auth!
    path('crash-test/', CrashTestView.as_view(), name='crash-test'),
]

