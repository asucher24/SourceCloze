import json

class ForbiddenError(Exception):
    def __init__(self, user, message="User is not allowed to access poll."):
        self.user = user
        self.message = message
        super().__init__(self.message)

    def __str__(self):
        return f'{self.user} -> {self.message}'


class ForbiddenExecution(Exception):
    def __init__(self, info, message="Execution not allowed"):
        self.info = info
        self.message = message
        super().__init__(self.message)

    def __str__(self):
        return f'{self.message}: {self.info}'
        

DEFAULT = object()
def from_req(request, keyId, default=DEFAULT):
    val = request.POST.get(keyId, None)
    if val is None:
        try:
            val = json.loads(request.body.decode('utf-8')).get(keyId, None)
        except Exception as e:
            print(e)
    if val is None:
        if default is DEFAULT:
            raise KeyError("keyId " + keyId)
        val = default
    return val


def clean_answer(string:str, replacefrom:str="  *", replaceto:str=" ")-> str:
    import re
    # string = re.sub(replacefrom, replaceto, string)
    string = string.strip()
    return string