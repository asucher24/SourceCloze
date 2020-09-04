"""sourcecloze URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.0/topics/http/urls/
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
from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path, re_path
from pages.views import base_forward
from django.shortcuts import render_to_response
def returnDoc(request):
    return render_to_response('build/html/index.html')

urlpatterns = [
    # path(r'^docs/', include('sphinxdoc.urls')),
    path('admin/doc/', include('django.contrib.admindocs.urls')),
    path('admin/', admin.site.urls),
    path('views/',  include('pages.urls', namespace='views')),
    path('api/',    include('poll_api.urls', namespace='api')),
    path('auth/',   include('authentication.urls', namespace='auth')),
    # path('admin/doc/',include('django.contrib.admindocs.urls')),
    # re_path(r'^docs/',  returnDoc),
    path('', base_forward),
] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
