import os
import re
import random
# import signal
import shutil
import string
import subprocess
import sys
import docker
import tarfile
import multiprocessing, time
from poll_api.models import ForbiddenExecText as ForbiddenRegex
from utils.utils import ForbiddenExecution
from utils.DockerData import DockerData
from sourcecloze.settings_base import DEFAULT_COMPILE_TIMEOUT_S
docker_data = DockerData()
interpreters = ['python', 'r']
langs = {
    'python':{'fileend':'py', 'command':'python'}, # will be executed in docker container!!!
    'r':{'fileend':'r', 'command':'Rscript'},  # will be executed in docker container!!!
    'java':{'fileend':'java', 'command':'/usr/bin/javac'},
    'c':{'fileend':'c', 'command':'/usr/bin/gcc'},
    'c++':{'fileend':'cpp', 'command':'/usr/bin/g++'},
    'javascript':{'fileend':'js', 'command':'/usr/bin/nodejs --check'},
}

syntax_result = {
    'None':'None', # ('?', 'unknown'),
    'False':'False',# ('-', 'failed'),
    'True':'True', # ('+', 'successful'),
    'Forbidden':'Forbidden',# ('x', 'forbidden'),
}
syntax_result_val = {
    'None':None, # ('?', 'unknown'),
    'False':False,# ('-', 'failed'),
    'True':True, # ('+', 'successful'),
    'Forbidden':'Forbidden',# ('x', 'forbidden'),
}
def check_answer_allowed(answer:str, regexpressions:list):
    for item in regexpressions:
        try:
            # print("Test: ", "(.*?)"+item.regex+"(.*?)")
            # regexp = re.compile("(.*?)"+item.regex+"(.*?)", re.IGNORECASE)
            regexp = re.findall("(.*?)"+item.regex+"(.*?)", answer, re.MULTILINE)
        except Exception:
            continue
            # raise Exception("Cannot check answer with regex's." \
                # + "Not a regular expression: " + item.regex)
        else:
            # print(regexp)
            # if regexp.match(answer):
            if len(regexp) > 0:
                print("Forbidden")
                raise ForbiddenExecution("FORBIDDEN: "+ answer + "--" + item.regex)



#####################
####  BUILDCODE #####
#####################
def build_code(ct, answers, lang):
    print("build code")
    # checking answers. do they contain forbidden expressions, than do not execute!
    for answer in answers:
        ct = re.sub('(CL\{)(.*?)(\}ZE)', answer, ct, 1)
        ct = re.sub('\{SOURCE\}', '', ct)
        ct = re.sub('\{SOURCEEND\}', '', ct)
    # answersStr = ''.join(answers)
    print("check allowed")
    check_answer_allowed(answer=ct, 
        regexpressions=ForbiddenRegex.objects.filter(language='all'))
    check_answer_allowed(answer=ct, 
        regexpressions=ForbiddenRegex.objects.filter(language=lang))
    return ct
def build_codeanswer(ct, lang, answer_i=0, answers=None):
    # for i in range(len(answers)):
    if answer_i>0:
        # print("Replacing", int(answer_i), "gap with original")
        ct = re.sub('(CL\{)', '', ct, answer_i)
        ct = re.sub('(\}ZE)', '', ct, answer_i)
    if answers:
        ct = re.sub('(CL\{)(.*?)(\}ZE)', answers[answer_i], ct, 1)
    ct = re.sub('(CL\{)', '', ct)
    ct = re.sub('(\}ZE)', '', ct)
    ct = re.sub('\{SOURCE\}', '', ct)
    ct = re.sub('\{SOURCEEND\}', '', ct)
    print("BUILDCODE: " + ct)
    check_answer_allowed(answer=ct, 
        regexpressions=ForbiddenRegex.objects.filter(language='all'))
    check_answer_allowed(answer=ct, 
        regexpressions=ForbiddenRegex.objects.filter(language=lang))
    return ct

def syntax_check_available(ctlang):
    return ctlang in langs.keys()


#####################
####  DO CHECKS #####
#####################
def do_syntax_check(ctlang, code):
    if not syntax_check_available(ctlang):
        print('\tNo such language ' + ctlang)
        raise Exception("Language not defined " + ctlang)
    if ctlang in interpreters:
        return run_docker(code, ctlang)
    return run_compiler(code, ctlang=ctlang)


def run_docker(code, ctlang):
    name = create_file(code, lang=ctlang)
    container = docker_data.get_container(lang=ctlang)
    res = run_in_container(container, filename=name, lang=ctlang)
    os.remove(name)
    shutil.rmtree(os.path.dirname(name), ignore_errors=True)
    return res

def run_compiler(code, ctlang):
    name = create_file(code, lang=ctlang)
    result = compile_sub(file=name, command=langs[ctlang]['command'])
    os.remove(name)
    shutil.rmtree(os.path.dirname(name), ignore_errors=True)
    return result


def compile_sub(file, command):
    result = None
    try:
        command = command.split(" ")
        command += [file]
        env = os.environ.copy()
        subprocess.check_call(command, env=env)
        result = True
    except Exception as e:
        result = False
    return result

###### Helper ######
def get_filename(content, lang):
    s = ""
    if lang=="java":
        s = 'class (\w+)'
    result = re.search(s, content)
    try:
        return result.group(1).strip()
    except Exception:
        return "check_{}".format(lang)

def generate_random_str(size=10):
    letters = string.ascii_lowercase
    return ''.join(random.choice(letters) for i in range(size))


def create_file(code, lang, fdirname=None):
    if not fdirname:
        fdirname = generate_random_str()
    absfile = os.path.join(
        docker_data.PATH_FILES,
        fdirname,
        get_filename(code, lang)+'.'+langs[lang]['fileend'])
    os.makedirs(os.path.dirname(absfile), exist_ok=True)
    #print("CODE: " + code)
    with open(absfile, "w") as f:
        f.write(code)
    return absfile



# def copy_to(container, src, dst):
#     os.chdir(os.path.dirname(src))
#     srcname = os.path.basename(src)
#     tar = tarfile.open(src + '.tar', mode='w')
#     try:
#         tar.add(srcname)
#     finally:
#         tar.close()
#     data = open(src + '.tar', 'rb').read()
#     container.put_archive(os.path.dirname(dst), data)
#     os.remove(src + '.tar')

def run_in_container(container, filename, lang, user="nobody"):
    def run(container, filename, lang, user, return_dict):
        try:
            filepath_relative = os.path.relpath(filename, start=docker_data.PATH_FILES)
            filepath_docker = os.path.join(docker_data.PATH_FILES_DOCKER, filepath_relative)
            # copy_to(container, src=filename, dst=filepath_docker)
            (exitcode, output) = container.exec_run(
                [langs[lang]['command'], filepath_docker], 
                user=user)
            print(container.short_id, "{}: {}".format(exitcode, output))
            return_dict[filename] = (exitcode == 0)
        except Exception as e:
            return_dict[filename] = None
            # print(container.short_id, str(e))
        return return_dict
    manager = multiprocessing.Manager()
    return_dict = manager.dict()
    p = multiprocessing.Process(target=run, args=(container, filename, lang, user, return_dict), name=filename)
    p.start()
    start = time.time()
    while time.time() - start <= DEFAULT_COMPILE_TIMEOUT_S:
        if not p.is_alive():  # All the processes are done, break now.
            break
        time.sleep(.1)  # Just to avoid hogging the CPU
    else:
        # We only enter this if we didn't 'break' above.
        print(container.short_id, "timed out, killing process")
        p.terminate()
        p.join()
        return_dict[filename] = None
    return return_dict[filename]
