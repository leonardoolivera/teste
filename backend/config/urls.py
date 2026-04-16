from django.contrib import admin
from django.urls import include, path
from drf_spectacular.views import SpectacularAPIView, SpectacularRedocView, SpectacularSwaggerView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/health/', include('apps.core.urls')),
    path('api/v1/core/', include('apps.core.api_urls')),
    path('api/v1/catalog/', include('apps.catalog.urls')),
    path('api/v1/users/', include('apps.users.urls')),
    path('api/v1/circulation/', include('apps.circulation.urls')),
    path('api/v1/inventory/', include('apps.inventory.urls')),
    path('api/v1/portal/', include('apps.portal.urls')),
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    path('api/docs/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
    path('api/redoc/', SpectacularRedocView.as_view(url_name='schema'), name='redoc'),
]
