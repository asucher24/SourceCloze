from django.contrib.auth import authenticate
# from authentication.models import User
from django.contrib.auth import get_user_model
from django.test import TestCase
from sourcecloze.settings_base import DEFAULT_FORBIDDEN_REGEX_FILE
from poll_api.models import ForbiddenExecText
import json
import re
import os
User = get_user_model()
# results': {
#                     'byBundle': sort_ca_by_bundle(ct, ca), 
#                     # = [{"clozes":[{"nr":"#1","code":"x"},{"nr":"#2","code":"y"},{"nr":"#3","code":"z"},{"nr":"#4","code":"a"}],"name":"Answer","percentage":"100%"}]
#                     'byEach': sort_ca_by_each(ct, ca)
#                 }}

class PagesTestCase(TestCase):
	def setUp(self):
		self.user = User.objects.create(username='testuser', password='12345', is_active=True, is_staff=True, is_superuser=False) 
		self.user.set_password('hello') 
		self.user.save()
		polldata = {
			'lang':'python',
			'name':'testcase-python-name',
			'count':'2',
			'code':'c=True\nif CL{c}ZE:\n\tprint(CL{"Hello"}ZE)',
			'answer':{'cloze_1':"1", 'cloze_2':"0"},
			'compile':'',
			'results':{
				'byBundle':[],
				'byEach':[]
			},
		}

		self.login()
		response = self._ajax(
			url='/api/start-poll/',
			data={'user': 'testuser',
				  'cloze_test': polldata['code'],
				  'cloze_count': polldata['count'],
				  'cloze_name': polldata['name'],
				  'language': polldata['lang']}
		)
		self.valid_pollid = self.assertEqualStatusCode(response, 200)['cloze_test_id']
		self.logout()

	def _ajax(self, url, data={}) -> str:
		return self.client.post(
			url,
			data=json.dumps(data),
			content_type='application/json',
			HTTP_X_REQUESTED_WITH='XMLHttpRequest',
			follow=True,
			secure=True
		)
	def assertEqualStatusCode(self, response,  status_code) -> str:
		self.assertEqual(response.status_code, status_code)
		json_string = response.content
		response_data = json.loads(json_string)
		return response_data

	def login(self):
		self.client.login(username='testuser', password='hello') 
	def logout(self):
		response = self._ajax('/auth/logout/')

	def test_show_resultview_notloggedin(self):
		response = self._ajax('/views/poll/'+self.valid_pollid+'/result')
		self.assertEquals(response.status_code, 200)
		self.assertTrue('Login with gitlab' in str(response.content))
	def test_show_resultview_loggedin(self):
		self.login()
		response = self._ajax('/views/poll/'+self.valid_pollid+'/result')
		self.assertEquals(response.status_code, 200)
		self.assertTrue('Welcome' in str(response.content))


	def test_show_pollview_notloggedin(self):
		response = self._ajax('/views/poll/'+self.valid_pollid+'')
		self.assertEquals(response.status_code, 200)
		self.assertTrue('Login with gitlab' in str(response.content))
	def test_show_pollview_loggedin(self):
		self.login()
		response = self._ajax('/views/poll/'+self.valid_pollid+'')
		self.assertEquals(response.status_code, 200)
		self.assertTrue('Welcome' in str(response.content))

	def test_show_createpoll_notloggedin(self):
		response = self._ajax('/views/poll')
		self.assertEquals(response.status_code, 200)
		self.assertTrue('Login with gitlab' in str(response.content))
	def test_show_createpoll_loggedin(self):
		self.login()
		response = self._ajax('/views/poll')
		self.assertEquals(response.status_code, 200)
		self.assertTrue('Welcome' in str(response.content))

	def test_show_polls_notloggedin(self):
		response = self._ajax('/views/', {})
		self.assertEquals(response.status_code, 200)
		self.assertTrue('Login with gitlab' in str(response.content))
	def test_show_polls_loggedin(self):
		self.login()
		response = self._ajax('/views/', {})
		self.assertEquals(response.status_code, 200)
		self.assertTrue('Welcome' in str(response.content))

	def test_baseview_notloggedin(self):
		response = self._ajax('/', {})
		self.assertEquals(response.status_code, 200)
		self.assertTrue('Enter poll ID' in str(response.content))
	def test_baseview_loggedin(self):
		self.login()
		response = self._ajax('/', {})
		self.assertEquals(response.status_code, 200)
		self.assertTrue('Welcome' in str(response.content))


	def test_homeforward_notloggedin(self):
		response = self._ajax('/views/id/'+self.valid_pollid+'/', {})
		self.assertEquals(response.status_code, 200)
		self.assertTrue(self.valid_pollid in str(response.content))
	def test_homeforward_loggedin(self):
		self.login()
		response = self._ajax('/views/id/'+self.valid_pollid+'/', {})
		self.assertEquals(response.status_code, 200)
		self.assertTrue(self.valid_pollid in str(response.content))
		self.assertTrue('Join' in str(response.content))

	def test_voteview_notloggedin(self):
		response = self._ajax('/views/vote/', {})
		self.assertEquals(response.status_code, 200)
		self.assertTrue('ID not found' in str(response.content))
	def test_viewsvote_loggedin(self):
		self.login()
		response = self._ajax('/views/vote/', {})
		self.assertEquals(response.status_code, 200)
		self.assertTrue('ID not found' in str(response.content))
	def test_viewsvote_noid(self):
		response = self._ajax('/views/vote/', {'cloze_test_id':self.valid_pollid})
		self.assertEquals(response.status_code, 200)
		self.assertTrue('summary-vote' in str(response.content))
	def test_viewsvote_inanctive(self):
		self.login()
		response = self._ajax('/api/deactivate-poll/', {'cloze_test_id':self.valid_pollid})
		self.assertEquals(response.status_code, 200)
		response = self._ajax('/views/vote/', {'cloze_test_id':self.valid_pollid})
		self.assertEquals(response.status_code, 200)
		self.assertTrue('not active' in str(response.content))


class PagesClozeAnswerTestCase(TestCase):
	def setUp(self):
		BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
		FILE = os.path.join(BASE_DIR, DEFAULT_FORBIDDEN_REGEX_FILE)

		data = {}
		with open(FILE, 'r', encoding="utf8") as f:
		    data = json.loads(re.sub("//.*","",f.read(),flags=re.MULTILINE))
		for (lang, regex_list) in data.items():
		    for regex in regex_list:
		        item, created = ForbiddenExecText.objects\
		            .get_or_create(language=lang, regex=regex)
		        if created:
		            item.save()
		self.user = User.objects.create(username='testuser', password='12345', is_active=True, is_staff=True, is_superuser=False) 
		self.user.set_password('hello') 
		self.user.save() 
		self.login()
	def login(self):
		self.client.login(username='testuser', password='hello') 
	def logout(self):
		response = self._ajax('/auth/logout/', {})

	def _ajax(self, url, data) -> str:
		return self.client.post(
			url,
			data=json.dumps(data),
			content_type='application/json',
			HTTP_X_REQUESTED_WITH='XMLHttpRequest',
			follow=True,
			secure=True
		)
	def assertEqualStatusCode(self, response,  status_code) -> str:
		self.assertEqual(response.status_code, status_code)
		json_string = response.content
		response_data = json.loads(json_string)
		return response_data
	def _start_poll(self, poll) -> str:
		# self.login()
		response = self._ajax(
			url='/api/start-poll/',
			data={'user': 'testuser',
				  'cloze_test': poll['code'],
				  'cloze_count': poll['count'],
				  'cloze_name': poll['name'],
				  'language': poll['lang']}
		)
		# self.logout()
		return self.assertEqualStatusCode(response, 200)

	def _sendStatus(self, pollId, ca, url='/views/status/'):
		return self._ajax(
			url= url,
			data={'cloze_test_id': pollId, 
				  'cloze_1': ca['cloze_1'], 
				  'cloze_2': ca['cloze_2'],
				  }
		)

	def _stop_poll(self, ct_id):
		# self.login()
		response = self._ajax(
			url='/api/stop-poll/',
			data={'cloze_test_id': ct_id}
		)
		# self.logout()
		return self.assertEqualStatusCode(response, 200)

	def check_poll(self, polldata):
		pollid = self._start_poll(polldata)['cloze_test_id']
		response = self._sendStatus(pollid, ca=polldata['answer'])
		self.assertTrue("Thanks" in str(response.content))
		self.assertTrue(polldata['compile'] in str(response.content))
		result = self._stop_poll(pollid)
		self.assertEqual(polldata['lang'], result['language'])
		self.assertEqual(polldata['results']['byBundle'], result['results']['byBundle'])
		self.assertEqual(polldata['results']['byEach'], result['results']['byEach'])
	# ########################################### Tests accessing pollId ###########################################
	
	def test_inactive_pollId(self):
		polldata = {
			'lang':'python',
			'name':'testcase-python-name',
			'count':'2',
			'code':'c=True\nif CL{c}ZE:\n\tprint(CL{"Hello"}ZE)',
			'answer':{'cloze_1':"1", 'cloze_2':"0"},
			'compile':'inactive',
			'results':{
				'byBundle':[],
				'byEach':[]
			},
		}
		pollid = self._start_poll(polldata)['cloze_test_id']
		response = self._ajax(
			url='/api/deactivate-poll/',
			data={'cloze_test_id': pollid},
		)
		self.assertEquals(response.status_code, 200)
		response = self._sendStatus(pollid, ca=polldata['answer'])
		self.assertTrue(polldata['compile'] in str(response.content))

	def test_no_pollId(self):
		response = self._ajax(
			url='/views/vote/',
			data={'cloze_1': 'foo', 'cloze_2': 'bar', 'cloze_test_i':'12345678'},
		)
		self.assertTrue("ID not found" in str(response.content))

	def test_no_pollId_status(self):
		# pollid = self._start_poll(polldata)['cloze_test_id']
		response = self._ajax(
			url= '/views/status/',
			data={'cloze_test_': "87654321", 
				# 'cloze_1': polldata['answer']['cloze_1'],
				# 'cloze': polldata['answer']['cloze_1'],
				}
		)
		self.assertTrue("ID not found" in str(response.content))

	def test_invalid_pollId(self):
		response = self._ajax(
			url='/views/vote/',
			data={'cloze_test_id': "88888888",
				  'cloze_1': 'a',
				  'cloze_2': 'b'},
		)
		self.assertTrue("ID not exists" in str(response.content))
	############################################ PYTHON  Tests answering poll  ###########################################
	def test_py_incomplete_pollId(self):
		polldata = {
			'lang':'python',
			'name':'testcase-python-name',
			'count':'2',
			'code':'c=True\nif CL{c}ZE:\n\tprint(CL{"Hello"}ZE)',
			'answer':{'cloze_1':"1"},
			'compile':'Please fill',
			'results':{
				'byBundle':[],
				'byEach':[]
			},
		}
		pollid = self._start_poll(polldata)['cloze_test_id']
		response = self._ajax(
			url= '/views/status/',
			data={'cloze_test_id': pollid, 
				'cloze_1': polldata['answer']['cloze_1'],
				# 'cloze': polldata['answer']['cloze_1'],
				}
		)
		self.assertTrue(polldata['compile'] in str(response.content))
	def test_py_valid_answer(self):
		print("\n\n\n\n\ntest valid answer")
		polldata = {
			'lang':'python',
			'name':'testcase-python-name',
			'count':'2',
			'code':'c=True\nif CL{c}ZE:\n\tprint(CL{"Hello"}ZE)',
			'answer':{'cloze_1':"1", 'cloze_2':"0"},
			'compile':'successfully',
			'results':{
				'byBundle':[{"clozes":[{"nr":"#1","code":"1"},{"nr":"#2","code":"0"}],"name":"Answer","percentage":100, 'syntaxcheck':'True'}],
				'byEach':[
					{"nr":"#1","clozes":[{"code":"1","percentage":100, 'syntaxcheck':'True'}]},
					{"nr":"#2","clozes":[{"code":"0","percentage":100, 'syntaxcheck':'True'}]}
				]
			},
		}
		self.check_poll(polldata)
	def test_py_invalid_answer(self):
		print("\n\n\n\n\ntest invalid answer")
		polldata = {
			'lang':'python',
			'name':'testcase-python-name',
			'count':'2',
			'code':'c=True\nif CL{c}ZE:\n\tprint(CL{"Hello"}ZE)',
			'answer':{'cloze_1':"1", 'cloze_2':"foo+1"},
			'compile':'wrong',
			'results':{
				'byBundle':[{"clozes":[{"nr":"#1","code":"1"},{"nr":"#2","code":"foo+1"}],"name":"Answer","percentage":100, 'syntaxcheck':'False'}],
				'byEach':[
					{"nr":"#1","clozes":[{"code":"1","percentage":100, 'syntaxcheck':'True'}]},
					{"nr":"#2","clozes":[{"code":"foo+1","percentage":100, 'syntaxcheck':'False'}]}
				]
			},
		}
		self.check_poll(polldata)
	def test_py_forbidden_answer(self):
		print("\n\n\n\n\ntest forbidden answer")
		polldata = {
			'lang':'python',
			'name':'testcase-python-name',
			'count':'2',
			'code':'c=True\nif CL{c}ZE:\n\tprint(CL{"Hello"}ZE)',
			'answer':{'cloze_1':"1", 'cloze_2':'"")\nimport os\nos.system("echo im eval") #'},
			'compile':'hack',
			'results':{
				'byBundle':[{"clozes":[{"nr":"#1","code":"1"},{"nr":"#2","code":'"")\nimport os\nos.system("echo im eval") #'}],"name":"Answer","percentage":100, 'syntaxcheck':'Forbidden'}],
				'byEach':[
					{"nr":"#1","clozes":[{"code":"1","percentage":100, 'syntaxcheck':'True'}]},
					{"nr":"#2","clozes":[{"code":'"")\nimport os\nos.system("echo im eval") #',"percentage":100, 'syntaxcheck':'Forbidden'}]}
				]
			},
		}
		self.check_poll(polldata)
	def test_py_endless_answer(self):
		print("\n\n\n\n\ntest endless answer")
		polldata = {
			'lang':'python',
			'name':'testcase-python-name',
			'count':'2',
			'code':'c=True\nif CL{c}ZE:\n\tprint(CL{"Hello"}ZE)',
			'answer':{'cloze_1':"1", 'cloze_2':"'')\nwhile(True):\n\tprint('endless')#"},
			'compile':'not compile',
			'results':{
				'byBundle':[{"clozes":[{"nr":"#1","code":"1"},{"nr":"#2","code":"'')\nwhile(True):\n\tprint('endless')#"}],"name":"Answer","percentage":100, 'syntaxcheck':'None'}],
				'byEach':[
					{"nr":"#1","clozes":[{"code":"1","percentage":100, 'syntaxcheck':'True'}]},
					{"nr":"#2","clozes":[{"code":"'')\nwhile(True):\n\tprint('endless')#","percentage":100, 'syntaxcheck':'None'}]}
				]
			},
		}
		self.check_poll(polldata)


	############################################ PYTHON  Tests answering poll  ###########################################
	def test_j_incomplete_pollId(self):
		polldata = {
			'lang':'java',
			'name':'tst-java',
			'count':'2',
			'code':'public class HelloWorld { '
				+ '{SOURCE} public static void helloWorld() { '
				+ 'System.out.println(CL{"1"}ZE); '
				+ 'System.out.println(CL{"2"}ZE); } {SOURCEEND} '
				+ 'public static void main (String[] args) { helloWorld(); } }',
			'answer':{'cloze_1':'"a"', 'cloze_2':'"b"'},
			'compile':'Please fill',
			'results':{},
		}
		polldata['results'] = {
			'byBundle':[{"clozes":[
				{"nr":"#1","code":polldata['answer']['cloze_1']},{"nr":"#2","code":polldata['answer']['cloze_2']}],
				"name":"Answer","percentage":100, 'syntaxcheck':'True'}],
			'byEach':[
				{"nr":"#1","clozes":[{"code":polldata['answer']['cloze_1'],"percentage":100, 'syntaxcheck':'True'}]},
				{"nr":"#2","clozes":[{"code":polldata['answer']['cloze_2'],"percentage":100, 'syntaxcheck':'True'}]}
			]}
		pollid = self._start_poll(polldata)['cloze_test_id']
		response = self._ajax(
			url= '/views/status/',
			data={'cloze_test_id': pollid, 
				'cloze_1': polldata['answer']['cloze_1'],
				# 'cloze': polldata['answer']['cloze_2'],
				}
		)
		self.assertTrue(polldata['compile'] in str(response.content))

	def test_j_valid_answer(self):
		polldata = {
			'lang':'java',
			'name':'tst-java',
			'count':'2',
			'code':'public class HelloWorld { '
				+ '{SOURCE} public static void helloWorld() { '
				+ 'System.out.println(CL{"1"}ZE); '
				+ 'System.out.println(CL{"2"}ZE); } {SOURCEEND} '
				+ 'public static void main (String[] args) { helloWorld(); } }',
			'answer':{'cloze_1':'"a"', 'cloze_2':'"b"'},
			'compile':'successfully',
			'results':{},
		}
		polldata['results'] = {
			'byBundle':[{"clozes":[
				{"nr":"#1","code":polldata['answer']['cloze_1']},{"nr":"#2","code":polldata['answer']['cloze_2']}],
				"name":"Answer","percentage":100, 'syntaxcheck':'True'}],
			'byEach':[
				{"nr":"#1","clozes":[{"code":polldata['answer']['cloze_1'],"percentage":100, 'syntaxcheck':'True'}]},
				{"nr":"#2","clozes":[{"code":polldata['answer']['cloze_2'],"percentage":100, 'syntaxcheck':'True'}]}
			]}
		self.check_poll(polldata)


	def test_py_invalid_answer(self):
		polldata = {
			'lang':'java',
			'name':'tst-java',
			'count':'2',
			'code':'public class HelloWorld { '
				+ '{SOURCE} public static void helloWorld() { '
				+ 'System.out.println(CL{"1"}ZE); '
				+ 'System.out.println(CL{"2"}ZE); } {SOURCEEND} '
				+ 'public static void main (String[] args) { helloWorld(); } }',
			'answer':{'cloze_1':'"a"', 'cloze_2':'foo'},
			'compile':'wrong',
			'results':{},
		}
		polldata['results'] = {
			'byBundle':[{"clozes":[
				{"nr":"#1","code":polldata['answer']['cloze_1']},{"nr":"#2","code":polldata['answer']['cloze_2']}],
				"name":"Answer","percentage":100, 'syntaxcheck':'False'}],
			'byEach':[
				{"nr":"#1","clozes":[{"code":polldata['answer']['cloze_1'],"percentage":100, 'syntaxcheck':'True'}]},
				{"nr":"#2","clozes":[{"code":polldata['answer']['cloze_2'],"percentage":100, 'syntaxcheck':'False'}]}
			]}
		self.check_poll(polldata)

	def test_py_forbidden_answer(self):
		polldata = {
			'lang':'java',
			'name':'tst-java',
			'count':'2',
			'code':'public class HelloWorld { '
				+ '{SOURCE} public static void helloWorld() { '
				+ 'System.out.println(CL{"1"}ZE); '
				+ 'System.out.println(CL{"2"}ZE); } {SOURCEEND} '
				+ 'public static void main (String[] args) { helloWorld(); } }',
			'answer':{'cloze_1':'"1"', 'cloze_2':'"exec(\'foo\')"'},
			'compile':'hack',
			'results':{},
		}
		polldata['results'] = {
			'byBundle':[{"clozes":[
				{"nr":"#1","code":polldata['answer']['cloze_1']},{"nr":"#2","code":polldata['answer']['cloze_2']}],
				"name":"Answer","percentage":100, 'syntaxcheck':'Forbidden'}],
			'byEach':[
				{"nr":"#1","clozes":[{"code":polldata['answer']['cloze_1'],"percentage":100, 'syntaxcheck':'True'}]},
				{"nr":"#2","clozes":[{"code":polldata['answer']['cloze_2'],"percentage":100, 'syntaxcheck':'Forbidden'}]}
			]}
		self.check_poll(polldata)

	# def test_py_endless_answer(self):
	# 	polldata = {
	# 		'lang':'java',
	# 		'name':'tst-java',
	# 		'count':'2',
	# 		'code':'public class HelloWorld { '
	# 			+ '{SOURCE} public static void helloWorld() { '
	# 			+ 'System.out.println(CL{"1"}ZE); '
	# 			+ 'System.out.println(CL{"2"}ZE); } {SOURCEEND} '
	# 			+ 'public static void main (String[] args) { helloWorld(); } }',
	# 		'answer':{'cloze_1':'"1"', 'cloze_2':'"");while(true){System.out.println("eval");}System.out.println(""'},
	# 		'compile':'not compile',
	# 		'results':{},
	# 	}
	# 	polldata['results'] = {
	# 		'byBundle':[{"clozes":[
	# 			{"nr":"#1","code":polldata['answer']['cloze_1']},{"nr":"#2","code":polldata['answer']['cloze_2']}],
	# 			"name":"Answer","percentage":100, 'syntaxcheck':'None'}],
	# 		'byEach':[
	# 			{"nr":"#1","clozes":[{"code":polldata['answer']['cloze_1'],"percentage":100, 'syntaxcheck':'True'}]},
	# 			{"nr":"#2","clozes":[{"code":polldata['answer']['cloze_2'],"percentage":100, 'syntaxcheck':'None'}]}
	# 		]}
	# 	self.check_poll(polldata)