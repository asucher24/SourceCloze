import hashlib
import random
import string
from django.db import transaction
from django.db.models import Count, F, Case, When, Value
from django.db.models.functions import Round
from poll_api.models import ClozeTest, ClozeAnswer
from utils.syntaxcheck import syntax_result, syntax_result_val, build_codeanswer, build_code, do_syntax_check#, syntax_check_available
from utils.utils import ForbiddenError, ForbiddenExecution
def get_hash(s:str) -> str:
    return hashlib.sha256(str.encode(s)).hexdigest()
    # >>> m = hashlib.md5()   # **new** hash object
    # >>> m.update('stackoverflow')
    # >>> m.hexdigest()
    # m = hashlib.md5()
    # m = hashlib.sha256()
    # m.update(str.encode(s))
    # return m.hexdigest()
    # return s

def isAlive(id) -> set:
    return (True, id)

def delete_cloze_test(ct_id, user):
    ClozeTest.objects.get(
        cloze_test_id__exact=ct_id, 
        cloze_creator__exact=get_hash(user))\
    .delete()
def delete_cloze_answers(ct_id, user): 
    if not (ClozeTest.objects \
        .filter(cloze_test_id__exact=ct_id, 
                cloze_creator__exact=get_hash(user)) \
        .exists()):
        raise ForbiddenError(user)
    ClozeAnswer.objects.filter(cloze_test_id__exact=ct_id).delete()

def random_string_generator(size=8, chars=string.digits) -> str:
    """
    Generates pseudo random string
    :param size: length of genrated string (default: 8)
    :param chars: allowed chars in generated string (default: 1-9)
    :return: pseudo random generated string
    """
    return ''.join(random.choice(chars) for _ in range(size))


def unique_cloze_test_id_generator() -> str:
    """
    Genereates unique cloze test id
    :return: generated cloze test id
    """
    new_ct_id = random_string_generator()
    # genrate recursive new cloze id until not in databsae
    if ClozeTest.objects.filter(cloze_test_id__exact=new_ct_id).exists():
        return unique_cloze_test_id_generator()
    return new_ct_id

def get_cloze_test(ct_id:str, user:str)->dict:
    """ 
    Access an existing poll
    :param ct_id: cloze test id (must be unique)
    :return: dict of poll information 
    """

    if not ClozeTest.objects.filter(cloze_test_id__exact=ct_id).exists():
        raise KeyError
        # return {'Error': 'Invalid Id'}
    ct = ClozeTest.objects.get(cloze_test_id__exact=ct_id)
    if get_hash(user) != ct.cloze_creator:
        raise ForbiddenError(user)
    return {
        'cloze_test_id': ct.cloze_test_id,
        'cloze_test': ct.cloze_test,
        'cloze_name': ct.cloze_name,
        'cloze_count': ct.cloze_count,
        'language': ct.language,
        'active': ct.active,
    }
    
def create_cloze_test(ct_id: str, ct: str, cloze_count: int, language: str,
                      ct_name: str, user:str):
    """
    Creates new entry in database
    :param ct_id: cloze test id (must be unique)
    :param ct: cloze test text
    :param cloze_count: number of clozes in cloze test
    :param language: programming language
    """
    # user = hashlib.sha224(user).hexdigest()
    ct = ClozeTest(cloze_test_id=ct_id,
                   cloze_test=ct,
                   cloze_name=ct_name,
                   cloze_creator=get_hash(user),
                   cloze_count=cloze_count,
                   language=language)
    ct.save()
def set_poll_status(ct_id:str, status:bool, user:str):
    """
    Reactivate poll
    """
    if not ClozeTest.objects.filter(cloze_test_id__exact=ct_id).exists():
        raise KeyError
        # return {'Error': 'Invalid Id'}
    ct = ClozeTest.objects.get(cloze_test_id__exact=ct_id)
    if get_hash(user) != ct.cloze_creator:
        raise ForbiddenError(user)
    ct.active = status
    ct.save()

def update_cloze_test(
                     user,
                     ct_id:str,
                     ct_name=None,
                     # cloze_creator=get_hash(user),
                     ct_test=None,
                     ct_count=None,
                     active=None,
                     language=None):
    """
    Update specific poll
    """
    if not ClozeTest.objects.filter(cloze_test_id__exact=ct_id).exists():
        raise Exception('Invalid Id')
    ct = ClozeTest.objects.get(cloze_test_id__exact=ct_id)
    if get_hash(user) != ct.cloze_creator:
        raise ForbiddenError(user)
    if ct_name:
        ct.cloze_name = ct_name
    if ct_count:
        ct.cloze_count = ct_count
    if active:
        ct.active = active
    if language:
        ct.language = language
    if ct_test:
        ct.cloze_test = ct_test
    ct.save()

def update_answers(user, ct_id, ct_answer, ca_num, ca_type, ca_result):

    if not ClozeTest.objects.filter(cloze_test_id__exact=ct_id).exists():
        raise Exception('Invalid Id')
    ct = ClozeTest.objects.get(cloze_test_id__exact=ct_id)
    if get_hash(user) != ct.cloze_creator:
        raise ForbiddenError(user)

    cas = ClozeAnswer.objects.filter(cloze_test=ct, cloze_num__exact=ca_num)
    for ca in cas:
        if ca.answer == ct_answer:
            ca.result = syntax_result[ca_result]
            ca.save()

def get_answer_count(ct_id:str, user:str) -> int:
    """
    Return the number of given answers
    """
    count = 0
    if not ClozeTest.objects.filter(cloze_test_id__exact=ct_id).exists():
        raise KeyError('Invalid Id')
        # return {'Error': 'Invalid Id'}
    ct = ClozeTest.objects.get(cloze_test_id__exact=ct_id)

    if get_hash(user) != ct.cloze_creator:
        raise ForbiddenError(user)
    with transaction.atomic():
        ca = ClozeAnswer.objects.filter(cloze_test=ct)
        try:
            count = 0
            if ct.cloze_count != 0:
                count = ca.count() / ct.cloze_count
        except Exception as dbz:
            print("Exception: ", str(dbz))
    return count

def evaluate_cloze_test(ct_id: str, user:str) -> dict:
    """
    Evaluates all answers for a specific cloze test id.
    success_dict:
    {results: [{clozes: [{nr: str, code: str}], name: str, percentage: str}]}
    failure_dict:
    {results: []}
    invalid_dict:
    {Error: str}
    :param ct_id: cloze test id
    :return: success_dict, failure_dict or invalid_dict
    """
    if not ClozeTest.objects.filter(cloze_test_id__exact=ct_id).exists():
        raise KeyError
        # return {'Error': 'Invalid Id'}
    ct = ClozeTest.objects.get(cloze_test_id__exact=ct_id)
    if get_hash(user) != ct.cloze_creator:
        raise ForbiddenError(user)
    # set cloze test to inactiv
    ct.active = False
    ct.save()

    with transaction.atomic():
        # get all answers for cloze test id
        ca = ClozeAnswer.objects.select_for_update().filter(cloze_test=ct)

    if not ca.exists():
        # return failure_dict if no answers are available
        return {'language': ct.language, 'results': []}
    response = {'language': ct.language, 
                'results': {
                    'byBundle': sort_ca_by_bundle(ct, ca),
                    'byEach': sort_ca_by_each(ct, ca)
                }}
    response['results']['byBundle'] = response_completion(
        response['results']['byBundle'], 
        len(ca) // ct.cloze_count)
    return response



def sort_ca_by_each(ct, ca):
    result = []
    answers_count = len(ca) / ct.cloze_count
    ca = ca.order_by('cloze_num')

    for ct_num in range(ct.cloze_count):
        clozes = ca.filter(cloze_num=ct_num+1) \
            .values(code=F('answer'), syntaxcheck=F('result')) \
            .annotate(percentage=Count('answer')/answers_count*100) \
            .annotate(percentage=Round('percentage')) \
            .order_by('-percentage')
        result.append({
            'nr':'#{}'.format(ct_num+1), 
            'clozes':list(clozes)}) # [{'code': '""', 'percentage': 40}, {'code': '', 'percentage': 20}, {'code': '2', 'percentage': 20}, {'code': 'x', 'percentage': 20}]

    return result
def fetch_syntax_result(ct, ca, i):
    # Just Temporary to correct result of answers on resolution:
    answers = ca[i:i+ct.cloze_count]
    for j in range(ct.cloze_count):
        answers[j] = answers[j].answer
        try:
            cloze_test = build_codeanswer(ct.cloze_test, ct.language, j, answers)
            is_correct = str(do_syntax_check(ct.language, cloze_test))
        except ForbiddenExecution as fe:
            print("Forbidden", fe)
            is_correct = "Forbidden"
        ca[i+j].result = syntax_result[is_correct]
        print("result_check", syntax_result[is_correct])
        ca[i+j].save()
        print('\n'*3)

def sort_ca_by_bundle(ct, ca):
    ca = ca.order_by('answer_id', 'cloze_num')
    match_str = ''
    results = []
    # go through every answer set (clozes per user)
    for i in range(0, len(ca), ct.cloze_count):
        match_str = ''
        # fetch_syntax_result(ct, ca, i)

        for j in range(i, i + ct.cloze_count):
            # erase whitespaces for answer matching
            match_str += ca[j].answer.replace(' ', '')

        # check if answer is already given
        match = False
        for e in results:
            if match_str == e['match_str']:
                # increment count for answer if matched
                e['count'] += 1
                match = True
                break
        if match:
            continue
        # add answer to response
        result_cloze = {'clozes': [], 'match_str': match_str, 'count': 1, 'syntaxcheck': True}
        for j in range(i, i + ct.cloze_count):
            result_cloze['clozes'].append({'nr': '#' + str(ca[j].cloze_num),
                                     'code': ca[j].answer})
            # merge syntaxcheck result of single answers
            if "Forbidden" in [ca[j].result, result_cloze['syntaxcheck']]:
                result_cloze['syntaxcheck'] = "Forbidden"
            else:
                result_cloze['syntaxcheck'] = result_cloze['syntaxcheck'] and syntax_result_val[ca[j].result]
        result_cloze['syntaxcheck'] = str(result_cloze['syntaxcheck'])
        results.append(result_cloze)
    return results

def response_completion(results: dict, answer_count: int) -> dict:
    """
    :param results: dictonary with all the results for cloze test
    :param answer_count: total count of answers for specific cloze test
    :return: success_dict
    """
    # sort results in reverse order by count
    results.sort(key=lambda x: x['count'], reverse=True)
    for r in results:
        r['name'] = 'Answer'
        try:
            r['percentage'] = round(0)
            if answer_count != 0:
                r['percentage'] = round(r['count'] / answer_count * 100)
        except Exception as dbz:
            print("Exception: ", str(dbz))
        r.pop('count')
        r.pop('match_str')
    return results
