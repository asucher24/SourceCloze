from django.http import JsonResponse
from django.http import HttpResponse, HttpResponseRedirect
from django.views.decorators.csrf import csrf_exempt
from utils.utils_poll_api import *
from utils.syntaxcheck import do_syntax_check, build_codeanswer
from django.http import Http404
from utils.utils_authentication import get_user
from utils.utils import from_req, ForbiddenError, ForbiddenExecution
from django.http import HttpResponseForbidden

@csrf_exempt
def start_poll(request):
    """
    Receive call from poll entity for starting poll. Needs a logged in user and a post request with specific parameter.
    
    Needs logged in user. 
    
    Parameter:

    :request: Request HTTP-POST

    :cloze_name(string, optional): HTTP-POST parameter: title of the poll

    :cloze_text(string, optional): HTTP-POST parameter: source code for the poll

    :cloze_count(string, optional): HTTP-POST parameter: count of gaps in cloze_text

    :language(string, optional): HTTP-POST parameter: language of cloze_text (e.g. python, java, c, c++, R) (optional)

    :active(boolean, optional): HTTP-POST parameter: status of the poll (optional)
    
    Returns one of the following:

    :HttpResponse: with status code on error

    :JsonResponse: if statuscode is 200; returns object with cloze_test_id 
    """
    if not request.user.is_authenticated:
        return HttpResponse("Please login.", status=401)  # HTTP_401_UNAUTHORIZED

    if request.method != 'POST':
        return HttpResponse("Invalid/Bad request", status=400)  # HttpResponseBadRequest

    # Generate new id for cloze test
    cloze_test_id = unique_cloze_test_id_generator()
    try:
        # Create new cloze test table in database
        create_cloze_test(ct_id=cloze_test_id,
                          ct=from_req(request, 'cloze_test'),
                          cloze_count=from_req(request, 'cloze_count'),
                          ct_name=from_req(request, 'cloze_name'),
                          user=get_user(request),
                          language=from_req(request, 'language'))
    except KeyError as ke:
        print(ke)
        return HttpResponse("Bad request. KeyError.", status=400)
    except Exception as e:
        return HttpResponse("Unknown error: {}".format(e), status=404)
    return JsonResponse({'cloze_test_id': cloze_test_id})
@csrf_exempt
def test_code(request):
    """
    Receive call from poll entity for test poll code. Depend on the language of 
    the source code it will be executed (Python, R) or compiled (Java, C, C++, JavaScript).
    Before excuting it will be checked for 'forbidden content'. 
    If code match any of regular expressions contains in :model: ForbiddenExecTexts,
    the result of the test, will be: Forbidden
    Otherwise: 'True' for successfully compiled/executed, 'False' for failed, 
    and 'None' if the execution took to long time (e.g. infinity loop)
    
    Needs logged in user. User have to be the creater of the poll.
    
    Parameter:

    :request: Request HTTP-POST
    
    :cloze_text(string, optional): HTTP-POST parameter: source code for the poll
    
    :language(string, optional): HTTP-POST parameter: language of cloze_text (e.g. python, java, c, c++, R) (optional)
        
    Returns one of the following:

    :HttpResponse: with status code on error

    :JsonResponse: if statuscode is 200; object with result contains one of the following 'True', 'False', 'None', 'Forbidden'
    """
    if not request.user.is_authenticated:
        return HttpResponse("Please login.", status=401)  # HTTP_401_UNAUTHORIZED
    try:
        lang = from_req(request, 'language')
        cloze_test = build_codeanswer(
            from_req(request, 'cloze_test'),
            lang
            )
        is_correct = str(do_syntax_check(lang, cloze_test))
    except KeyError:
        return HttpResponse("Bad request. KeyError cloze_test_id", status=400)
    except ForbiddenExecution as fe:
        is_correct = "Forbidden"
    return JsonResponse({'result':is_correct})
    
@csrf_exempt
def get_poll(request):
    """
    Receive call from poll entity for getting poll information including all attributes.
    
    Needs logged in user. User have to be the creater of the poll.
    
    Parameter:

    :request: Request HTTP-POST

    :cloze_text_id(string): 8 digits as string (existing poll id)
    
    Returns one of the following:

    :HttpResponse: with status code on error

    :JsonResponse: if statuscode is 200; including poll object
    
    """
    if not request.user.is_authenticated:
        return HttpResponse("Please login.", status=401)  # HTTP_401_UNAUTHORIZED
    
    if request.method != 'POST':
        return HttpResponse("Invalid/Bad request", status=400)  # HttpResponseBadRequest
    try:
        ct_id = from_req(request, 'cloze_test_id')
    except KeyError:
        return HttpResponse("Bad request. KeyError cloze_test_id", status=400)
    try:
        poll = get_cloze_test("{}".format(ct_id), user=get_user(request))
    except KeyError:
        return HttpResponse("Poll {} does not exist".format(ct_id), status=404)
    except ForbiddenError as fe:
        return HttpResponseForbidden(str(fe))
    except Exception as e:
        return HttpResponse("Unknown error: {}".format(e), status=404)
    return JsonResponse(poll)

@csrf_exempt
def update_poll(request):
    """
    Receive call from poll entity for updating an existing poll. Only update the given parameter
    
    Needs logged in user. User have to be the creater of the poll.
    
    Parameter:

    :request: Request HTTP-POST
    
    :next(string, optional): HTTP-GET parameter: define the redirect url 

    :cloze_text_id(string): 8 digits as string (existing poll id)

    :cloze_name(string, optional): HTTP-POST parameter: title of the poll
    
    :cloze_text(string, optional): HTTP-POST parameter: source code for the poll
    
    :cloze_count(string, optional): HTTP-POST parameter: count of gaps in cloze_text
    
    :language(string, optional): HTTP-POST parameter: language of cloze_text (e.g. python, java, c, c++, R) (optional)
    
    :active(boolean, optional): HTTP-POST parameter: status of the poll (optional)
    
    Returns one of the following:

    :HttpResponse: with status code on error

    :JsonResponse: if statuscode is 200 and next is not set
    
    :HttpsResponseRedirect: if HTTP-GET Param 'next' is set
    """
    if not request.user.is_authenticated:
        return HttpResponse("Please login.", status=401)  # HTTP_401_UNAUTHORIZED
    
    if request.method != 'POST':
        return HttpResponse("Invalid/Bad request", status=400)  # HttpResponseBadRequest
    try:
        cloze_test_id = from_req(request, 'cloze_test_id')
    except KeyError:
        return HttpResponse("Bad request. KeyError cloze_test_id", status=400)
    try:
        update_cloze_test(
            user=get_user(request),
            ct_id=cloze_test_id,
            ct_name=from_req(request, 'cloze_name', default=None),
            ct_test=from_req(request, 'cloze_test', default=None),
            ct_count=from_req(request, 'cloze_count', default=None),
            active=from_req(request, 'active', default=None),
            language=from_req(request, 'language', default=None))
    except ForbiddenError as fe:
        return HttpResponseForbidden(str(fe))
    except KeyError as e:
        return HttpResponse("Bad request. KeyError. e", status=400)
    except Exception as e:
        return HttpResponse("Unknown error: {}".format(e), status=404)

    next = request.GET.get('next', None)
    if next:
        return HttpResponseRedirect(next)
    return JsonResponse({'Error': ''})


@csrf_exempt
def update_answer_result(request):
    """
    Receive call from poll entity for updating the syntax check result of an existing answer.
    
    Needs logged in user. User have to be the creater of the poll.
    
    Parameter:

    :request: Request HTTP-POST
    
    :cloze_text_id(string): 8 digits as string (existing poll id)

    :cloze_answer(string): HTTP-POST parameter: answer of the poll
    
    :syntaxresult(string): HTTP-POST parameter: result of the syntax check for given answer ('False', 'True', 'None', 'Forbidden')
    
    :answer_type(string, optional): HTTP-POST parameter: 'byEach'
    
    Returns one of the following:

    :HttpResponse: with status code on error

    :JsonResponse: if statuscode is 200 and next is not set
    """
    if not request.user.is_authenticated:
        return HttpResponse("Please login.", status=401)  # HTTP_401_UNAUTHORIZED
    
    if request.method != 'POST':
        return HttpResponse("Invalid/Bad request", status=400)  # HttpResponseBadRequest
    try:
        cloze_test_id = from_req(request, 'cloze_test_id')
    except KeyError:
        return HttpResponse("Bad request. KeyError cloze_test_id", status=400)
    try:
        update_answers(
            user=get_user(request),
            ct_id=cloze_test_id,
            ct_answer=from_req(request, 'cloze_answer'),
            ca_num=from_req(request, 'answer_num'),
            ca_type=from_req(request, 'answer_type', default='byEach'),
            ca_result=from_req(request, 'syntaxresult'))
        result = evaluate_cloze_test(cloze_test_id, user=get_user(request))
        result['poll'] = get_cloze_test("{}".format(cloze_test_id), user=get_user(request))
    
    except ForbiddenError as fe:
        return HttpResponseForbidden(str(fe))
    except KeyError as e:
        return HttpResponse("Bad request. KeyError. "+ e, status=400)
    except Exception as e:
        return HttpResponse("Unknown error: {}".format(e), status=404)
    return JsonResponse(result)

@csrf_exempt
def activate_poll(request):
    """
    Receive call from poll entity for activate poll (again)
    
    Needs logged in user. User have to be the creater of the poll.
    
    Parameter:

    :request: Request HTTP-POST
    
    :next(string, optional): HTTP-GET parameter: define the redirect url 

    :cloze_text_id(string): 8 digits as string (existing poll id)
        
    Returns one of the following:

    :HttpResponse: with status code on error

    :JsonResponse: if statuscode is 200 and next is not set; contains poll object

    :HttpsResponseRedirect: if HTTP-GET Param 'next' is set
    
    """
    if not request.user.is_authenticated:
        return HttpResponse("Please login.", status=401)  # HTTP_401_UNAUTHORIZED

    if request.method != 'POST':
        return HttpResponse("Invalid/Bad request", status=400)  # HttpResponseBadRequest
    try:
        ct_id = from_req(request, 'cloze_test_id')
    except KeyError:
        return HttpResponse("Bad request. KeyError cloze_test_id", status=400)
    try:
        set_poll_status(ct_id, True, user=get_user(request))
        poll = get_cloze_test("{}".format(ct_id), user=get_user(request))
    except ForbiddenError as fe:
        return HttpResponseForbidden(str(fe))
    except KeyError:
        return HttpResponse("Poll does not exist", status=404)
    except Exception as e:
        return HttpResponse("Unknown error: {}".format(e), status=404)

    next = request.GET.get('next', None)
    if next:
        return HttpResponseRedirect(next)
    return JsonResponse(poll)
    # return JsonResponse({'Error': ''})

@csrf_exempt
def deactivate_poll(request):
    """
    Receive call from poll entity for deactivate poll without to calculate resolution
    
    Needs logged in user. User have to be the creater of the poll.
    
    Parameter:

    :request: Request HTTP-POST
    
    :next(string, optional): HTTP-GET parameter: define the redirect url 

    :cloze_text_id(string): 8 digits as string (existing poll id) 
        
    Returns one of the following:

    :HttpResponse: with status code on error

    :JsonResponse: if statuscode is 200 and next is not set

    :HttpsResponseRedirect: if HTTP-GET Param 'next' is set
    
    """
    if not request.user.is_authenticated:
        return HttpResponse("Please login.", status=401)  # HTTP_401_UNAUTHORIZED

    if request.method != 'POST':
        return HttpResponse("Invalid/Bad request", status=400)  # HttpResponseBadRequest
    try:
        ct_id = from_req(request, 'cloze_test_id')
    except KeyError:
        return HttpResponse("Bad request. KeyError cloze_test_id", status=400)
    try:
        set_poll_status(ct_id, False, user=get_user(request))
    except ForbiddenError as fe:
        return HttpResponseForbidden(str(fe))
    except KeyError:
        return HttpResponse("Poll does not exist", status=404)
    except Exception as e:
        return HttpResponse("Unknown error: {}".format(e), status=404)

    next = request.GET.get('next', None)
    if next:
        return HttpResponseRedirect(next)
    return JsonResponse({'Error': ''})

@csrf_exempt
def status_poll(request):
    """
    Receive call from poll entity for getting the count of answers dor a specific poll id
    
    Needs logged in user. User have to be the creater of the poll.
    
    Parameter:

    :request: Request HTTP-POST
    
    :next(string, optional): HTTP-GET parameter: define the redirect url 

    :cloze_text_id(string): 8 digits as string (existing poll id)

    Returns one of the following:

    :HttpResponse: with status code on error

    :JsonResponse: if statuscode is 200; contains object with cloze_answer_count
    """
    if not request.user.is_authenticated:
        return HttpResponse("Please login.", status=401)  # HTTP_401_UNAUTHORIZED
        
    if request.method != 'POST':
        return HttpResponse("Invalid/Bad request", status=400)
    try:
        ct_id = from_req(request, 'cloze_test_id')
    except KeyError:
        return HttpResponse("Bad request. KeyError cloze_test_id", status=400)

    try:
        answer_count = get_answer_count(ct_id, user=get_user(request))
    except ForbiddenError as fe:
        return HttpResponseForbidden(str(fe))
    except KeyError:
        return HttpResponse("Poll does not exist", status=404)
        # return KeyError({'Error': 'Invalid Id'})
        # return JsonResponse({'Error': 'Invalid Id'})
    except Exception as e:
        return HttpResponse("Unknown error: {}".format(e), status=404)
    # Evaluate cloze test and return results
    return JsonResponse({"cloze_answer_count":answer_count})


@csrf_exempt
def stop_poll(request):
    """
    Receive call from poll entity for stoping poll. Calcating percentage for answers in two formats:
    byBundle and byEach. 
    ByBundle calculates percentage for whole unique answers. byEach calculates percentage per gap in cloze.
    
    Needs logged in user. User have to be the creater of the poll.
    
    Parameter:

    :request: Request HTTP-POST
    
    :cloze_text_id(string): 8 digits as string (existing poll id)
        
    Returns one of the following:

    :HttpResponse: with status code on error

    :JsonResponse: if statuscode is 200; return the poll result object

    Returned Format additional to poll information:

    'results':{
        'byBundle':[{"clozes":[{"nr":"#1","code":"answer1.1"},{"nr":"#2","code":"answer1.2"}],"name":"Answer","percentage":100, 'syntaxcheck':'False'}],
        'byEach':[
            {"nr":"#1","clozes":[{"code":"answer1.1","percentage":100, 'syntaxcheck':'True'}]},
            {"nr":"#2","clozes":[{"code":"answer1.2","percentage":100, 'syntaxcheck':'False'}]}
        ]
    },


    """
    if not request.user.is_authenticated:
        return HttpResponse("Please login.", status=401)

    if request.method != 'POST':
        return HttpResponse("Invalid/Bad request", status=400)
    try:
        ct_id = from_req(request, 'cloze_test_id')
    except KeyError:
        return HttpResponse("Bad request. KeyError cloze_test_id", status=400)

    try:
        result = evaluate_cloze_test(ct_id, user=get_user(request))
        result['poll'] = get_cloze_test("{}".format(ct_id), user=get_user(request))
    except ForbiddenError as fe:
        return HttpResponseForbidden(str(fe))
    except KeyError:
        # return HttpResponse("Poll does not exist", status=404)
        return JsonResponse({'Error': 'Invalid Id'})
    except Exception as e:
        return HttpResponse("Unknown error: {}".format(e), status=404)
    # Evaluate cloze test and return results
    return JsonResponse(result)

@csrf_exempt
def delete_poll_answers(request):
    """
    Receive call from poll entity for delete poll answers. Has no effect to poll object.
    
    Needs logged in user. User have to be the creater of the poll.
    
    Parameter:

    :request: Request HTTP-POST
    
    :next(string, optional): HTTP-GET parameter: define the redirect url 

    :cloze_text_id(string): 8 digits as string (existing poll id)
    
    Returns one of the following:

    :HttpResponse: with status code on error
    :JsonResponse: if statuscode is 200 and next is not set
    :HttpsResponseRedirect: if HTTP-GET Param 'next' is set
    
    """
    if not request.user.is_authenticated:
        return HttpResponse("Please login.", status=401)  # HTTP_401_UNAUTHORIZED
    if request.method != 'POST':
        return HttpResponse("Invalid/Bad request", status=400)  # HttpResponseBadRequest
    try:
        ct_id = from_req(request, 'cloze_test_id')
    except KeyError:
        return HttpResponse("Bad request. KeyError cloze_test_id", status=400)
    user = get_user(request)
    try:
        delete_cloze_answers(ct_id, user=user)
    except Exception:
        return HttpResponse("Could not delete poll", status=404)

    next = request.GET.get('next', None)
    if next:
        return HttpResponseRedirect(next)
    return HttpResponse("deleted poll answers", status=200)

@csrf_exempt
def delete_poll(request):
    """
    Receive call from poll entity for delete poll. This can not be undone.
    
    Needs logged in user. User have to be the creater of the poll.

    Parameter:

    :request: Request HTTP-POST
    
    :next(string, optional): HTTP-GET parameter: define the redirect url 

    :cloze_text_id(string): 8 digits as string (existing poll id)
    
    Returns one of the following:

    :HttpResponse: with status code on error

    :JsonResponse: if statuscode is 200 and next is not set
    
    :HttpsResponseRedirect: if HTTP-GET Param 'next' is set
    """
    if not request.user.is_authenticated:
        return HttpResponse("Please login.", status=401)  # HTTP_401_UNAUTHORIZED
    if request.method != 'POST':
        return HttpResponse("Invalid/Bad request", status=400)  # HttpResponseBadRequest
    try:
        ct_id = from_req(request, 'cloze_test_id')
    except KeyError:
        return HttpResponse("KeyError: cloze_test_id", status=404)
    user = get_user(request)
    try:
        delete_cloze_test(ct_id, user)
    except Exception:
        return HttpResponse("Could not delete poll", status=404)

    next = request.GET.get('next', None)
    if next:
        return HttpResponseRedirect(next)
    return HttpResponse("deleted poll", status=200)
