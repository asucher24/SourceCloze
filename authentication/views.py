from django.contrib.auth import logout as auth_logout
from django.http import HttpResponseRedirect
from django.shortcuts import render

def login_view(request):
    """
    Shows an login page

    Return a rendered template of :template:`login.html`
    
    """
    return render(request, 'login.html', {}) 

def logout(request):

    """
    Logout the user

    Redirects to :view:`pages.create-poll-view`    
    """
    auth_logout(request)
    next = request.GET.get('/views/next', '/views/poll')
    return HttpResponseRedirect(next)