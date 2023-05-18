"""config URL Configuration.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
import django_saml2_auth.views
from django.contrib import admin
from django.urls import include, path
from rest_framework_jwt.views import refresh_jwt_token
from rest_framework_simplejwt import views as jwt_views

from account.backends import acs, signin
from common.views import signin_okta

urlpatterns = [
    path("saml2_auth/acs/", acs),
    path("admin/login/", signin_okta),
    path(r"jwt_refresh", refresh_jwt_token),
    path(
        "auth/token/", jwt_views.TokenObtainPairView.as_view(), name="token_obtain_pair"
    ),
    path(
        "auth/token/refresh/",
        jwt_views.TokenRefreshView.as_view(),
        name="token_refresh",
    ),
    # path('admin/', admin.site.urls),
    # path("api/account/", include("account.urls")),
    path("api/common/", include("common.urls")),
    path("api/account/", include("account.urls")),
]
