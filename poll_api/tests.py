from django.contrib.auth import authenticate
from django.contrib.auth import get_user_model
# from authentication.models import User
from django.test import TestCase
from sourcecloze.settings_base import DEFAULT_FORBIDDEN_REGEX_FILE
from poll_api.models import ForbiddenExecText
import json
import re
import os
User = get_user_model()
class PollApiViewTestCase(TestCase):
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

		self.user = User.objects.create(username='testuser2', password='12345', is_active=True, is_staff=True, is_superuser=False) 
		self.user.set_password('hello') 
		self.user.save() 
		self.polldata = {
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
				  'cloze_test': self.polldata['code'],
				  'cloze_count': self.polldata['count'],
				  'cloze_name': self.polldata['name'],
				  'language': self.polldata['lang']}
		)
		self.valid_pollid = self.assertEqualStatusCode(response, 200)['cloze_test_id']
		self.logout()

	def login(self, name="testuser"):
		self.client.login(username=name, password='hello') 
	def logout(self):
		response = self._ajax('/auth/logout/', {})

	def _ajax(self, url, data={}, method='post') -> str:
		if (method=='post'):
			return self.client.post(
				url,
				data=json.dumps(data),
				content_type='application/json',
				HTTP_X_REQUESTED_WITH='XMLHttpRequest',
				secure=True
			)
		return self.client.get(
				url,
				data=data,
				content_type='application/json',
				HTTP_X_REQUESTED_WITH='XMLHttpRequest',
				secure=True
			)
	def assertEqualStatusCode(self, response,  status_code) -> str:
		self.assertEqual(response.status_code, status_code)
		json_string = response.content
		response_data = json.loads(json_string)
		return response_data
	def _start_poll(self, poll, method='post') -> str:
		response = self._ajax(
			method=method,
			url='/api/start-poll/',
			data={'user': poll.get('user', "testuser"),
				  'cloze_test': poll['code'],
				  'cloze_count': poll['count'],
				  'cloze_name': poll['name'],
				  'language': poll['lang']}
		)
		return self.assertEqualStatusCode(response, 200)

	# ########################################### Tests api/start_poll ###########################################
	def test_start_poll_unauthorized(self):
		response = self._ajax('/api/start-poll/')
		self.assertEquals(response.status_code, 401)
		self.assertTrue('Please login' in str(response.content))
	def test_start_poll_notpost(self):
		self.login()
		response = self._ajax('/api/start-poll/', method='get')
		self.assertEquals(response.status_code, 400)
		self.assertTrue('Invalid/Bad request' in str(response.content))
		self.logout()
	def test_start_poll_valid_poll(self):
		self.login()
		polldata = {
			'language':'python',
			'cloze_name':'tst-py',
			'cloze_count':'2',
			'cloze_test':'if CL{1}ZE:\n\tprint(CL{"1"}ZE)',
		}
		response = self._ajax('/api/start-poll/', data=polldata)
		response_data = self.assertEqualStatusCode(response, 200)
		self.assertTrue('cloze_test_id' in response_data)
		self.assertEqual(8, len(response_data['cloze_test_id']))
		self.logout()
	def test_start_poll_invalid_langkey(self):
		self.login()
		polldata = { 'foolang':'python', 'cloze_name':'tst-py',
			'cloze_count':'2', 'cloze_test':'if CL{1}ZE:\n\tprint(CL{"1"}ZE)',
		}
		response = self._ajax('/api/start-poll/', data=polldata)
		self.assertEquals(response.status_code, 400)
		self.assertTrue('Bad request' in str(response.content))
		self.logout()
	def test_start_poll_invalid_namekey(self):
		self.login()
		polldata = { 'language':'python', 'fooname':'tst-py',
			'cloze_count':'2', 'cloze_test':'if CL{1}ZE:\n\tprint(CL{"1"}ZE)',
		}
		response = self._ajax('/api/start-poll/', data=polldata)
		self.assertEquals(response.status_code, 400)
		self.assertTrue('Bad request' in str(response.content))
		self.logout()
	def test_start_poll_invalid_countkey(self):
		self.login()
		polldata = { 'language':'python', 'cloze_name':'tst-py',
			'foocount':'2', 'cloze_test':'if CL{1}ZE:\n\tprint(CL{"1"}ZE)',
		}
		response = self._ajax('/api/start-poll/', data=polldata)
		self.assertEquals(response.status_code, 400)
		self.assertTrue('Bad request' in str(response.content))
		self.logout()

	def test_start_poll_invalid_codekey(self):
		self.login()
		polldata = { 'language':'python', 'cloze_name':'tst-py',
			'count':'2', 'foocode':'if CL{1}ZE:\n\tprint(CL{"1"}ZE)',
		}
		response = self._ajax('/api/start-poll/', data=polldata)
		self.assertEquals(response.status_code, 400)
		self.assertTrue('Bad request' in str(response.content))
		self.logout()



	# ########################################### Tests api/test_poll ###########################################
	def test_test_code_unauthorized(self):
		response = self._ajax('/api/test-code/')
		self.assertEquals(response.status_code, 401)
		self.assertTrue('Please login' in str(response.content))
	def test_test_code_invalid_languagekey(self):
		self.login()
		polldata = {
			'foolanguage':'python',
			'cloze_test':'if CL{1}ZE:\n\tprint(CL{"1"}ZE)',
		}
		response = self._ajax('/api/test-code/', data=polldata)
		self.assertEquals(response.status_code, 400)
		self.assertTrue('Bad request' in str(response.content))
		self.logout()

	def test_test_code_invalid_clozetestkey(self):
		self.login()
		polldata = {
			'language':'python',
			'foocloze_test':'if CL{1}ZE:\n\tprint(CL{"1"}ZE)',
		}
		response = self._ajax('/api/test-code/', data=polldata)
		self.assertEquals(response.status_code, 400)
		self.assertTrue('Bad request' in str(response.content))
		self.logout()

	def test_test_code_valid(self):
		self.login()
		polldata = {
			'language':'python',
			'cloze_test':'if CL{1}ZE:\n\tprint(CL{"1"}ZE)',
		}
		response = self._ajax('/api/test-code/', data=polldata)
		response_data = self.assertEqualStatusCode(response, 200)
		self.assertTrue('result' in response_data)
		self.assertEqual('True', response_data['result'])
		self.logout()

	def test_test_code_invalid(self):
		self.login()
		polldata = {
			'language':'python',
			'cloze_test':'if CL{1}ZE\n\tprint(CL{"1"}ZE)',
		}
		response = self._ajax('/api/test-code/', data=polldata)
		response_data = self.assertEqualStatusCode(response, 200)
		self.assertTrue('result' in response_data)
		self.assertEqual('False', response_data['result'])
		self.logout()

	def test_test_code_forbidden(self):
		self.login()
		polldata = {
			'language':'python',
			'cloze_test':'if CL{1}ZE:\n\tprint(CL{)\nimport os\nos.system("eval"}ZE)',
		}
		response = self._ajax('/api/test-code/', data=polldata)
		response_data = self.assertEqualStatusCode(response, 200)
		self.assertTrue('result' in response_data)
		self.assertEqual('Forbidden', response_data['result'])
		self.logout()

	# ########################################### Tests api/get_poll ###########################################
	def test_get_poll_unauthorized(self):
		response = self._ajax('/api/get-poll/', {'cloze_test_id':self.valid_pollid})
		self.assertEquals(response.status_code, 401)
		self.assertTrue('Please login' in str(response.content))

	def test_get_poll_notpost(self):
		self.login()
		response = self._ajax('/api/get-poll/', method='get')
		# response = self._ajax('/api/get-poll/', {'cloze_test_id':self.valid_pollid})
		self.assertEquals(response.status_code, 400)
		self.assertTrue('Invalid/Bad request' in str(response.content))
		self.logout()
	def test_get_poll_invalid_clozeidkey(self):
		self.login()
		response = self._ajax('/api/get-poll/', {'Foocloze_test_id':self.valid_pollid})
		self.assertEquals(response.status_code, 400)
		self.assertTrue('Bad request' in str(response.content))
		self.logout()

	def test_get_poll_forbidden(self):
		self.login("testuser2")
		response = self._ajax('/api/get-poll/', {'cloze_test_id':self.valid_pollid})
		self.assertEquals(response.status_code, 403)
		# self.assertTrue('Forbidden' in str(response.content))
		self.logout()
	def test_get_poll_valid(self):
		self.login()
		response = self._ajax('/api/get-poll/', {'cloze_test_id':self.valid_pollid})
		response_data = self.assertEqualStatusCode(response, 200)
		self.assertTrue('cloze_test_id' in response_data)
		self.assertTrue('language' in response_data)
		self.assertTrue('cloze_count' in response_data)
		self.assertTrue('cloze_name' in response_data)
		self.assertTrue('cloze_test' in response_data)
		self.assertEqual(self.valid_pollid, response_data['cloze_test_id'])
		self.assertEqual(self.polldata['lang'], response_data['language'])
		self.assertEqual(int(self.polldata['count']), response_data['cloze_count'])
		self.assertEqual(self.polldata['name'], response_data['cloze_name'])
		self.assertEqual(self.polldata['code'], response_data['cloze_test'])
		self.logout()


	# ########################################### Tests api/update_poll ###########################################
	def test_update_poll_unauthorized(self):
		# pollid = self._start_poll(self.polldata)['cloze_test_id']
		response = self._ajax('/api/update-poll/')
		self.assertEquals(response.status_code, 401)
		self.assertTrue('Please login' in str(response.content))
	def test_update_poll_notpost(self):
		self.login()
		# pollid = self._start_poll(self.polldata)['cloze_test_id']
		response = self._ajax('/api/update-poll/', method='get')
		self.assertEquals(response.status_code, 400)
		self.assertTrue('Invalid/Bad request' in str(response.content))
		self.logout()
	def test_update_poll_valid_poll(self):
		self.login()
		pollid = self._start_poll(self.polldata)['cloze_test_id']
		polldata = {
			'language':'python',
			'cloze_name':'tst-py',
			'cloze_count':'2',
			'cloze_test_id':pollid,
			'cloze_test':'if CL{1}ZE:\n\tprint(CL{"1"}ZE)',
		}
		response = self._ajax('/api/update-poll/', data=polldata)
		response_data = self.assertEqualStatusCode(response, 200)
		self.assertTrue('Error' in response_data)
		self.assertEqual('', response_data['Error'])
		self.logout()
		# self.assertTrue('language' in response_data)
		# self.assertTrue('cloze_count' in response_data)
		# self.assertTrue('cloze_name' in response_data)
		# self.assertTrue('cloze_test' in response_data)
		# self.assertEqual(polldata['language'], response_data['language'])
		# self.assertEqual(int(polldata['cloze_count']), response_data['cloze_count'])
		# self.assertEqual(polldata['cloze_name'], response_data['cloze_name'])
		# self.assertEqual(polldata['cloze_test'], response_data['cloze_test'])
	def test_update_poll_invalid_langkey(self):
		self.login()
		pollid = self._start_poll(self.polldata)['cloze_test_id']
		polldata = { 'foolang':'python', 'cloze_name':'tst-py','cloze_test_id':pollid,
			'cloze_count':'2', 'cloze_test':'if CL{1}ZE:\n\tprint(CL{"1"}ZE)',
		}
		response = self._ajax('/api/update-poll/', data=polldata)
		response_data = self.assertEqualStatusCode(response, 200)
		# self.assertEquals(response.status_code, 400)
		# self.assertTrue('Bad request' in str(response.content))
		self.logout()
	def test_update_poll_invalid_namekey(self):
		self.login()
		pollid = self._start_poll(self.polldata)['cloze_test_id']
		polldata = { 'language':'python', 'fooname':'tst-py','cloze_test_id':pollid,
			'cloze_count':'2', 'cloze_test':'if CL{1}ZE:\n\tprint(CL{"1"}ZE)',
		}
		response = self._ajax('/api/update-poll/', data=polldata)
		response_data = self.assertEqualStatusCode(response, 200)
		# self.assertEquals(response.status_code, 400)
		# self.assertTrue('Bad request' in str(response.content))
		self.logout()
	def test_update_poll_invalid_countkey(self):
		self.login()
		pollid = self._start_poll(self.polldata)['cloze_test_id']
		polldata = { 'language':'python', 'cloze_name':'tst-py','cloze_test_id':pollid,
			'foocount':'2', 'cloze_test':'if CL{1}ZE:\n\tprint(CL{"1"}ZE)',
		}
		response = self._ajax('/api/update-poll/', data=polldata)
		response_data = self.assertEqualStatusCode(response, 200)
		# self.assertEquals(response.status_code, 400)
		# self.assertTrue('Bad request' in str(response.content))
		self.logout()
	def test_update_poll_invalid_codekey(self):
		self.login()
		pollid = self._start_poll(self.polldata)['cloze_test_id']
		polldata = { 'language':'python', 'cloze_name':'tst-py','cloze_test_id':pollid,
			'count':'2', 'foocode':'if CL{1}ZE:\n\tprint(CL{"1"}ZE)',
		}
		response = self._ajax('/api/update-poll/', data=polldata)
		response_data = self.assertEqualStatusCode(response, 200)
		# self.assertEquals(response.status_code, 400)
		# self.assertTrue('Bad request' in str(response.content))
		self.logout()
	def test_update_poll_invalid_clozeidkey(self):
		self.login()
		pollid = self._start_poll(self.polldata)['cloze_test_id']
		polldata = { 'language':'python', 'cloze_name':'tst-py', 'Foocloze_test_id':pollid,
			'count':'2', 'foocode':'if CL{1}ZE:\n\tprint(CL{"1"}ZE)',
		}
		response = self._ajax('/api/update-poll/', data=polldata)
		self.assertEquals(response.status_code, 400)
		self.assertTrue('Bad request' in str(response.content))
		self.logout()





	# ########################################### Tests api/activate_poll ###########################################
	def test_activate_poll_unauthorized(self):
		response = self._ajax('/api/activate-poll/', {'cloze_test_id':self.valid_pollid})
		self.assertEquals(response.status_code, 401)
		self.assertTrue('Please login' in str(response.content))

	def test_activate_poll_notpost(self):
		self.login()
		response = self._ajax('/api/activate-poll/', method='get')
		# response = self._ajax('/api/activate-poll/', {'cloze_test_id':self.valid_pollid})
		self.assertEquals(response.status_code, 400)
		self.assertTrue('Invalid/Bad request' in str(response.content))
		self.logout()
	def test_activate_poll_invalid_clozeidkey(self):
		self.login()
		response = self._ajax('/api/activate-poll/', {'Foocloze_test_id':self.valid_pollid})
		self.assertEquals(response.status_code, 400)
		self.assertTrue('Bad request' in str(response.content))
		self.logout()
	def test_activate_poll_invalid_pollid(self):
		self.login()
		response = self._ajax('/api/activate-poll/', {'cloze_test_id':'12345687'})
		self.assertEquals(response.status_code, 404)
		self.assertTrue('not exist' in str(response.content))
		self.logout()
	def test_activate_poll_forbidden(self):
		self.login("testuser2")
		response = self._ajax('/api/activate-poll/', {'cloze_test_id':self.valid_pollid})
		self.assertEquals(response.status_code, 403)
		# self.assertTrue('Forbidden' in str(response.content))
		self.logout()
	def test_activate_poll_valid(self):
		self.login()
		response = self._ajax('/api/activate-poll/', {'cloze_test_id':self.valid_pollid})
		response_data = self.assertEqualStatusCode(response, 200)
		self.assertTrue('cloze_test_id' in response_data)
		self.assertTrue('language' in response_data)
		self.assertTrue('cloze_count' in response_data)
		self.assertTrue('cloze_name' in response_data)
		self.assertTrue('cloze_test' in response_data)
		self.assertEqual(self.valid_pollid, response_data['cloze_test_id'])
		self.assertEqual(self.polldata['lang'], response_data['language'])
		self.assertEqual(int(self.polldata['count']), response_data['cloze_count'])
		self.assertEqual(self.polldata['name'], response_data['cloze_name'])
		self.assertEqual(self.polldata['code'], response_data['cloze_test'])
		self.logout()


	# ########################################### Tests api/activate_poll ###########################################
	def test_deactivate_poll_unauthorized(self):
		response = self._ajax('/api/deactivate-poll/', {'cloze_test_id':self.valid_pollid})
		self.assertEquals(response.status_code, 401)
		self.assertTrue('Please login' in str(response.content))

	def test_deactivate_poll_notpost(self):
		self.login()
		response = self._ajax('/api/deactivate-poll/', method='get')
		# response = self._ajax('/api/deactivate-poll/', {'cloze_test_id':self.valid_pollid})
		self.assertEquals(response.status_code, 400)
		self.assertTrue('Invalid/Bad request' in str(response.content))
		self.logout()
	def test_deactivate_poll_invalid_clozeidkey(self):
		self.login()
		response = self._ajax('/api/deactivate-poll/', {'Foocloze_test_id':self.valid_pollid})
		self.assertEquals(response.status_code, 400)
		self.assertTrue('Bad request' in str(response.content))
		self.logout()
	def test_deactivate_poll_invalid_pollid(self):
		self.login()
		response = self._ajax('/api/deactivate-poll/', {'cloze_test_id':'13245687'})
		self.assertEquals(response.status_code, 404)
		self.assertTrue('not exist' in str(response.content))
		self.logout()
	def test_deactivate_poll_forbidden(self):
		self.login("testuser2")
		response = self._ajax('/api/deactivate-poll/', {'cloze_test_id':self.valid_pollid})
		self.assertEquals(response.status_code, 403)
		# self.assertTrue('Forbidden' in str(response.content))
		self.logout()
	def test_deactivate_poll_valid(self):
		self.login()
		response = self._ajax('/api/deactivate-poll/', {'cloze_test_id':self.valid_pollid})
		response_data = self.assertEqualStatusCode(response, 200)
		self.assertTrue('Error' in response_data)
		self.assertEqual('', response_data['Error'])
		self.logout()

	# ########################################### Tests api/status_poll ###########################################
	def test_status_poll_unauthorized(self):
		response = self._ajax('/api/status-poll/')
		self.assertEquals(response.status_code, 401)
		self.assertTrue('Please login' in str(response.content))
	def test_status_poll_notpost(self):
		self.login()
		response = self._ajax('/api/status-poll/', method='get')
		# response = self._ajax('/api/deactivate-poll/', {'cloze_test_id':self.valid_pollid})
		self.assertEquals(response.status_code, 400)
		self.assertTrue('Invalid/Bad request' in str(response.content))
		self.logout()
	def test_status_poll_invalid_clozetestkey(self):
		self.login()
		response = self._ajax('/api/status-poll/', {'foocloze_test_id':self.valid_pollid})
		self.assertEquals(response.status_code, 400)
		self.assertTrue('Bad request' in str(response.content))
		self.logout()
	def test_status_poll_forbidden(self):
		self.login("testuser2")
		response = self._ajax('/api/status-poll/', {'cloze_test_id':self.valid_pollid})
		self.assertEquals(response.status_code, 403)
		# self.assertTrue('Forbidden' in str(response.content))
		self.logout()
	def test_status_poll_valid(self):
		self.login()
		response = self._ajax('/api/status-poll/', {'cloze_test_id':self.valid_pollid})
		response_data = self.assertEqualStatusCode(response, 200)
		self.assertTrue('cloze_answer_count' in response_data)
		self.assertEqual(0.0, response_data['cloze_answer_count'])
		self.logout()

	# ########################################### Tests api/stop_poll ###########################################
	def test_stop_poll_unauthorized(self):
		response = self._ajax('/api/stop-poll/')
		self.assertEquals(response.status_code, 401)
		self.assertTrue('Please login' in str(response.content))
	def test_stop_poll_notpost(self):
		self.login()
		response = self._ajax('/api/stop-poll/', method='get')
		# response = self._ajax('/api/deactivate-poll/', {'cloze_test_id':self.valid_pollid})
		self.assertEquals(response.status_code, 400)
		self.assertTrue('Invalid/Bad request' in str(response.content))
		self.logout()
	def test_stop_poll_invalid_clozetestkey(self):
		self.login()
		response = self._ajax('/api/stop-poll/', {'foocloze_test_id':self.valid_pollid})
		self.assertEquals(response.status_code, 400)
		self.assertTrue('Bad request' in str(response.content))
		self.logout()
	def test_stop_poll_forbidden(self):
		self.login("testuser2")
		response = self._ajax('/api/stop-poll/', {'cloze_test_id':self.valid_pollid})
		self.assertEquals(response.status_code, 403)
		# self.assertTrue('Forbidden' in str(response.content))
		self.logout()
	def test_stop_poll_valid_0answers(self):
		self.login()
		response = self._ajax('/api/stop-poll/', {'cloze_test_id':self.valid_pollid})
		response_data = self.assertEqualStatusCode(response, 200)
		self.assertEqual(self.polldata['lang'], response_data['language'])
		self.assertEqual([], response_data['results'])
		self.logout()
