from django.db import transaction
from django.db.models import Max, F, Q, Count, IntegerField,  ExpressionWrapper
from poll_api.models import ClozeTest, ClozeAnswer
from utils.utils_poll_api import get_hash

@transaction.atomic
def save_answers(cloze_test, answers, sid):
    """
    Save answer for cloze test to database
    :param cloze_test: ClozeTest model
    :param answer: answer text
    """
    ca = ClozeAnswer.objects\
        .select_for_update()\
        .filter(cloze_test=cloze_test)
    a_id = 0
    if ca:
        a_id = ca.aggregate(Max('answer_id'))['answer_id__max'] + 1
    cas = {}
    for i in range(len(answers)):
        new_ca = ClozeAnswer(answer_id=a_id,
                             cloze_num=i + 1,
                             cloze_test=cloze_test,
                             answer=answers[i],
                             sid=sid
                             )
        cas[i+1] = new_ca
        new_ca.save()
    return cas

def already_voted(sid, ct):
    """
    Checks if answer exist for given session id
    :param sid: Session ID
    :param cloze_test: specifiy the cloze test for checking
    :return: bool
    """
    if not sid:
        return False
    return ClozeAnswer.objects.filter(cloze_test=ct, sid__exact=sid).exists()
def is_poll_creator(user, ct):
    return ct.cloze_creator == get_hash(user)
    
def exists(cloze_test_id):
    """
    Checks if cloze test for id exists
    :param cloze_test_id: Poll ID
    :param message_type: neutral / failure / success
    :return: bool
    """
    return ClozeTest.objects\
        .filter(cloze_test_id__exact=cloze_test_id)\
        .exists()


def get_cloze_test(cloze_test_id):
    """
    Get ClozeTest model
    :param cloze_test_id: Poll ID
    :return: ClozeTest model
    """
    return ClozeTest.objects.get(cloze_test_id__exact=cloze_test_id)


def get_cloze_tests(user):
    """
    Get all ClozeTest for given user(hash)
    :param user: hashed username
    :return: ClozeTest models
    """
    # return list(ClozeTest.objects\
    #   .filter(cloze_creator__exact=get_hash(user)).values())
    # return list(ClozeTest.objects.values())
    
    return  list(ClozeTest.objects\
        .filter(cloze_creator__exact=get_hash(user))\
        .values() \
        .annotate(answer_count=\
            ExpressionWrapper( \
                Count('clozeanswer',  filter=Q(clozeanswer__cloze_test_id=F('cloze_test_id'))) \
                / F('cloze_count'), output_field=IntegerField() ) \
        ) \
        )
            #  )  \
        # .annotate(answers=F('answers') / F('cloze_count')) \