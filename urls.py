from django.contrib import admin
from django.urls import path, include
from rest_framework.authtoken.views import obtain_auth_token

urlpatterns = [
    path('admin/', admin.site.urls),
    path('auth/', include('djoser.urls')),
    path('auth/', include('djoser.urls.authtoken')),
    path('token/login/', obtain_auth_token, name='obtain_auth_token'),
    path('api/', include('LittleLemonAPI.urls')),
]
