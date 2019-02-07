"""itysk URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.10/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf.urls import url, include
from django.contrib import admin as tysk_admin

urlpatterns = [
    url(r'^tysk/admin/', tysk_admin.site.urls),
    # https://stackoverflow.com/questions/48608894/specifying-a-namespace-in-include-without-providing-an-app-name
    # url(r'^tysk/', include('tysk.urls', namespace="tysk")),
    url(r'^tysk/', include(('tysk.urls', 'tysk'), namespace="tysk")),
    url(r'^tysk/accounts/', include('allauth.urls')),
]
