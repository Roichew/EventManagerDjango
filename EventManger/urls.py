
from django.contrib import admin
from django.urls import path, include
from api.views import CreateNewUserView, CustomTokenObtainPairView
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from django.conf import settings
from django.conf.urls.static import static
from django.views.generic import RedirectView


urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include('api.urls')),  # Include the API URLs
    path('user/register/', CreateNewUserView.as_view(), name='user-register'),
    path("api/token/", CustomTokenObtainPairView.as_view(), name="get_token"),
    path("api/token/refresh/", TokenRefreshView.as_view(), name="refresh"),
    path('api-auth/', include('rest_framework.urls')),  # Include DRF authentication URLs
    path('', RedirectView.as_view(url='/api/events/', permanent=False)),

]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)