from django.contrib import admin
from django.db import models

class ClozeTestAdmin(admin.ModelAdmin):
    list_display = ('cloze_test_id','cloze_creator','cloze_name', 'language','active','cloze_count', 'cloze_test')
class ClozeTest(models.Model):
    """
    Stores a poll
    """
    cloze_test_id = models.CharField(max_length=12, primary_key=True)
    cloze_creator = models.CharField(max_length=255)
    cloze_name = models.CharField(max_length=255)
    cloze_test = models.TextField()
    cloze_count = models.PositiveSmallIntegerField()
    language = models.CharField(max_length=25)
    active = models.BooleanField(default=True)

    def __str__(self):
        return "TEST: id({}), count({}), name({}), language({}), active({})".format(
            self.cloze_test_id, self.cloze_count, self.cloze_name, self.language, self.active)

class ClozeAnswerAdmin(admin.ModelAdmin):
    list_display = ('answer_id', 'cloze_num', 'cloze_test','answer', 'result')
class ClozeAnswer(models.Model):
    """
    Stores a single answer for a poll cloze gap, related to :model:`poll_api.ClozeTest`
    """
    SYNTAXRESULT = (
        ('True', 'successful'),
        ('False', 'failed'),
        ('Forbidden', 'forbidden'),
        ('None', 'unknown'),
    )
    answer_id = models.PositiveSmallIntegerField()
    cloze_num = models.PositiveSmallIntegerField()
    cloze_test = models.ForeignKey(ClozeTest, on_delete=models.CASCADE)
    answer = models.CharField(max_length=255)
    sid = models.CharField(max_length=255, default="xxxxx")
    result = models.CharField(
        max_length=10,
        choices=SYNTAXRESULT,
        blank=False,
        default='?',
        help_text='Complete answer of syntax check. Manuelly set only to "?"',
    )
    class Meta:
        unique_together = (('answer_id', 'cloze_num', 'cloze_test'),)
    def __str__(self):
        return "ANSWER: aid({}), cnum({}), a({}), ct({})".format(
            self.answer_id, self.cloze_num, self.answer, self.cloze_test)

class ForbiddenExecTextAdmin(admin.ModelAdmin):
    list_display = ('language','regex')
class ForbiddenExecText(models.Model):
    """
    Stores regular expressions which disable source code execution if matched with langage
    """
    LANGUAGES = (
        ('all', 'all'),
        ('python', 'python'),
        ('java', 'Java'),
        ('r', 'R'),
        ('c', 'C'),
        ('c++', 'C++'),
        ('javascript', 'JavaScript'),
    )

    id = models.AutoField(primary_key=True)
    regex = models.CharField(max_length=255)
    language = models.CharField(
        max_length=25,
        choices=LANGUAGES,
        blank=False,
        default='a',
        help_text='programming language or "all"',
    )
        
    class Meta:
        unique_together = (('language', 'regex'),)
