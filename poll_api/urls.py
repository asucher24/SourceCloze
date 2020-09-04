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
from django.urls import  path
from poll_api.views import *


app_name = 'poll_api'

urlpatterns = [
    # path('check-answers/', check_answers, name='check-answers'),
    path('test-code/', test_code, name='test-code'),
    path('get-poll/', get_poll, name='get-poll'),
    path('start-poll/', start_poll, name='start-poll'),
    path('update-answer-result/', update_answer_result, name='update-answer-result'),
    path('update-poll/', update_poll, name='update-poll'),
    path('stop-poll/', stop_poll, name='stop-poll'),
    path('status-poll/', status_poll, name='status-poll'),
    path('activate-poll/', activate_poll, name='activate-poll'),
    path('deactivate-poll/', deactivate_poll, name='deactivate-poll'),
    path('delete-poll/', delete_poll, name='delete-poll'),
    path('delete-poll-answers/', delete_poll_answers, name='delete-poll-answers'),
] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
