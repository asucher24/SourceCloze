from django.contrib import messages
from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.template import loader
from sourcecloze.settings_base import URL
from utils.syntaxcheck import syntax_result, do_syntax_check, build_code, build_codeanswer
from utils.utils_authentication import get_user
from utils.utils_pages import *
from utils.utils import clean_answer, ForbiddenExecution, from_req
# from poll_api.utils import get_cloze_test


#===========Admin-View==============
def show_polls_view(request):
    """
    Return a rendered template of the poll overview. Contains all user specific polls with the poll information
    
    If user is not logged in a redirect to the login :template:`login.html` page will be triggered with the current url as parameter next
    
    Parameter:

    :request: HTTP request

    Returns one of the following:

    :HttpResponse: with rendered template :template:`polloverview.html`
    :HttpResponse: with rendered template :template:`login.html`
    """
    if not request.user.is_authenticated:
        context = {'next': '/views/'}
        return render(request, 'login.html', context)

    user = get_user(request)
    context = {
               'user': request.user,
               'polls': get_cloze_tests(user),
               }

    return render(request, 'polloverview.html', context)


def create_poll_view(request):
    """
    Return a rendered template of the poll creation view
    
    If user is not logged in a redirect to the login :template:`login.html` page will be triggered with the current url as parameter next
    
    Parameter:

    :request: HTTP request

    :cloze_text_id(string): 8 digits as string (existing poll id)

    Returns one of the following:

    :HttpResponse: with rendered template :template:`poll_creation/src/index.html`
    :HttpResponse: with rendered template :template:`login.html`
    """
    if not request.user.is_authenticated:
        context = {'next': '/views/poll/'}
        return render(request, 'login.html', context)
    
    context = {'user': request.user, 'url':URL}
    template = loader.get_template('poll_creation/src/index.html')
    return HttpResponse(template.render(context, request))

def show_poll_result_view(request, id):
    """
    Return a rendered template of the poll resolution view
    
    If user is not logged in a redirect to the login :template:`login.html` page will be triggered with the current url as parameter next
    
    Parameter:

    :request: HTTP request

    :cloze_text_id(string): 8 digits as string (existing poll id)

    Returns one of the following:

    :HttpResponse: with rendered template :template:`poll_creation/src/index.html`
    :HttpResponse: with rendered template :template:`login.html`
    """
    if not request.user.is_authenticated:
        context = {'next': '/views/poll/{}/'.format(id)}
        return render(request, 'login.html', context)
    
    context = {'user': request.user, 'ct_id': str(id), 'url':URL, 'resultview':True}
    template = loader.get_template('poll_creation/src/index.html')
    return HttpResponse(template.render(context, request))

def show_poll_view(request, id):
    """
    Return a rendered template of the poll access view
    
    If user is not logged in a redirect to the login :template:`login.html` page will be triggered with the current url as parameter next
    
    Parameter:

    :request: HTTP request

    :cloze_text_id(string): 8 digits as string (existing poll id)

    Returns one of the following:

    :HttpResponse: with rendered template :template:`poll_creation/src/index.html`
    :HttpResponse: with rendered template :template:`login.html`
    """
    if not request.user.is_authenticated:
        context = {'next': '/views/poll/{}/'.format(id)}
        return render(request, 'login.html', context)
        
    context = {'user': request.user, 'ct_id': str(id), 'url':URL}
    template = loader.get_template('poll_creation/src/index.html')
    return HttpResponse(template.render(context, request))


#===========Participant-View==============
def status(request, message_type, header, text):
    """
    Render the view, which is visible after answering the poll. Adds a message of syntax check result
    
    Parameter:

    :request: Request HTTP-POST

    :request: HTTP request

    :message_type(string): neutral / failure / success

    :header(string): message header

    :text(string): message text
    
    Returns one of the following:

    :HttpResponse: with rendered template :template:`status.html`
    """
    return render(request,
                  'status.html',
                  {'message': {
                        'type': message_type,
                        'header': header,
                        'text': text
                  }})


def home_view(request, *args, **kwargs):
    """
    Render the view, which is the home view of participation. Shows inputfield for poll id
    
    Parameter:

    :request: HTTP request

    Returns one of the following:

    :HttpResponse: with rendered template :template:`status.html`
    """
    return render(request, 'home.html', {})


def base_forward(request, *args, **kwargs):
    """
    Render home view called from url root path: '/'
    If user is logged in shows the poll overview otherwise the participation view
    
    Parameter:

    :request: HTTP request

    Returns one of the following:

    :HttpResponse: :template:`home.html` or :template: `polloverview.html`
    """
    if not request.user.is_authenticated:
        return render(request, 'home.html', {})
    user = get_user(request)
    context = {'user': request.user, 'polls': get_cloze_tests(user)}
    return render(request, 'polloverview.html', context)


def home_forward(request, id, *args, **kwargs):
    """
    Render the view, which is available throught the QR code. Shows the input field with the poll id.
    
    Parameter:

    :request: HTTP request

    :cloze_text_id(string): 8 digits as string (existing poll id)

    Returns one of the following:

    :HttpResponse: with rendered template :template:`home.html`
    """
    return render(request, 'home.html', {'id': str(id)})

def vote_view(request, *args, **kwargs):
    """
    Render the view, which is allows the participation for given poll id. Shows cloze_test.
    
    Parameter:

    :request: HTTP request
    
    :cloze_text_id(string): 8 digits as string (existing poll id)

    Returns one of the following:

    :HttpRedirect: redirects to :view:`pages.home`
    """
    try:
        cloze_test_id = from_req(request, 'cloze_test_id')
        cloze_test_id = clean_answer(cloze_test_id, " *", "")
    except KeyError:
        messages.error(request, 'Cloze ID not found.')
        return redirect('views:home')
    
    if exists(cloze_test_id):
        ct = get_cloze_test(cloze_test_id)
        if ct.active:
            print("Already votes?")
            if request.user.is_authenticated and is_poll_creator(get_user(request), ct):
                pass
            elif already_voted(request.COOKIES.get('usid',None), ct):
                messages.error(request, 'You have already voted.')
                return redirect('views:home')
            content = {'cloze_test_id': ct.cloze_test_id,
                       'code': ct.cloze_test,
                       'cloze_count': [i+1 for i in range(ct.cloze_count)],
                       'language': ct.language,
                       # 'user':get_user_details
                       }
            return render(request, 'vote.html', content)
        else:
            messages.error(request, 'Voting for cloze not active')
            # print('Voting for this Session ID not acitve')
            return redirect('views:home')
    # messages.error(request, 'Session ID not correct.')
    messages.error(request, 'Cloze ID not exists.')
    # print('Session ID not correct')
    return redirect('views:home')

def status_view(request, *args, **kwargs):
    """
    Render the view, which is visible after answering the poll
    
    Needs logged in user. 
    
    Parameter:

    :request: HTTP reequest

    :cloze_text_id(string): 8 digits as string (existing poll id)

    Returns one of the following:

    :HttpResponse: with rendered template :template:`status.html`
    """
    try:
        cloze_test_id = from_req(request, 'cloze_test_id')
        cloze_test_id = clean_answer(cloze_test_id, " *", "")
    except KeyError:
        return status(request, 'failure', 'Error', 'Cloze ID not found.')
    
    if not exists(cloze_test_id):
        return status(request, 'failure', 'Error', 'Cloze ID not exists.')

    ct = get_cloze_test(cloze_test_id)
    if not ct.active:
        return status(request, 'failure', 'Cloze test inactive',
                      'Voting no longer available')
    try:
        if request.user.is_authenticated:
            if is_poll_creator(get_user(request), ct):
                pass
            else:
                print("request ", request)
                print("SESSION", request.session)
                print("SESSION id ", request.session.get('usid', None))
                if already_voted(request.COOKIES.get('usid', None), ct):
                    messages.error(request, 'You have already voted.')
                    return redirect('views:home')
        else:
            if already_voted(request.COOKIES.get('usid', None), ct):
                messages.error(request, 'You have already voted.')
                return redirect('views:home')
    except Exception:
        pass
    answers = []
    for i in range(ct.cloze_count):
        try:
            cloze_i = from_req(request, 'cloze_' + str(i + 1))
        except KeyError:
            return status(request, 'neutral', 'Incomplete',
                          'Please fill in all the clozes')
            
        cloze_i = clean_answer(cloze_i)
        answers.append(cloze_i)
        if answers[-1] == '' or answers[-1].isspace():
            answers[-1] = ""
    sid = request.session._get_or_create_session_key()
    cas = save_answers(ct, answers, sid)
    try:
        cloze_test = build_code(ct.cloze_test, answers, ct.language)
        print("1TEST: ", cloze_test)
        is_correct_merged = str(do_syntax_check(ct.language, cloze_test))
    except ForbiddenExecution as fe:
        is_correct_merged = "Forbidden"
    print("1RESULT: ", is_correct_merged, type(is_correct_merged))
    if ct.cloze_count > 1 and is_correct_merged != "True":
        # print("First check is not successful")
        is_correct = ['']*ct.cloze_count
        for i in range(ct.cloze_count):
            print('\n'*3)
            try:
                cloze_test = build_codeanswer(
                    ct.cloze_test, ct.language, i, answers)
                is_correct[i] = str(do_syntax_check(ct.language, cloze_test))
            except ForbiddenExecution as fe:
                is_correct[i] = "Forbidden"
    else:
        is_correct = [is_correct_merged]*ct.cloze_count
    for i in range(ct.cloze_count):
        cas[i+1].result = syntax_result[is_correct[i]]
        cas[i+1].save()

    # Result of unit tests depends on message words: 'not compile', 'wrong', 'hack', 'successfully'
    response = status(request, 'success', 'Thanks for Voting!', 'Unknown Result of compiling: ' + is_correct_merged)
    if is_correct_merged == "None":
        response = status(request, 'success', 'Thanks for Voting!', 'Could not compile the code.')
    elif is_correct_merged == "False":
        response = status(request, 'success', 'Thanks for Voting!',
                  'Something in your syntax was wrong.')
    elif is_correct_merged == "Forbidden":
        response = status(request, 'success', 'Thanks for Voting!',
                  'Dont try to hack the system ;-).')
    elif is_correct_merged == "True":
        response = status(request, 'success', 'Thanks for Voting! :)', 
            'Code compiled successfully. {}'.format(
                '' if ct.language != 'python' else ''))
    response.set_cookie('usid', sid)
    return response