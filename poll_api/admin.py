from django.contrib import admin
from .models import *

admin.site.register(ClozeTest, ClozeTestAdmin)
admin.site.register(ClozeAnswer, ClozeAnswerAdmin)
admin.site.register(ForbiddenExecText, ForbiddenExecTextAdmin)