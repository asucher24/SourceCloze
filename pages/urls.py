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
from django.urls import path
from pages.views import *

app_name = 'pages'

urlpatterns = [
    path('home/', home_view, name='home'),
    path('poll/', create_poll_view, name='create-poll-view'),
    path('poll/<id>/result', show_poll_result_view, name='show-poll-result-view'),
    path('poll/<id>/', show_poll_view, name='show-poll-view'),
    path('id/<id>/', home_forward, name='home-forward'),
    path('vote/', vote_view, name='vote'),
    path('status/', status_view, name='status'),
    path('', show_polls_view, name='show-polls-view'),
] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
