# from .models import User
from django.contrib.auth import get_user_model
User = get_user_model()
from django.test import TestCase
import json
class PagesClozeAnswerTestCase(TestCase):
	def setUp(self):
		self.user = User.objects.create(username='testuser', password='12345', is_active=True, is_staff=True, is_superuser=True) 
		self.user.set_password('hello') 
		self.user.save()

	def _ajax(self, url, data) -> str:
		return self.client.post(
			url,
			data=json.dumps(data),
			content_type='application/json',
			HTTP_X_REQUESTED_WITH='XMLHttpRequest',
			follow=True,
			secure=True
		)

	def test_login(self):
		response = self._ajax('/auth/loginview/', {})
		self.assertEquals(response.status_code, 200)
		self.assertTrue('Login with gitlab' in str(response.content))
		# Log the user in
		self.client.login(username='testuser', password='hello') 
		response = self._ajax('/auth/loginview/', {})
		self.assertEquals(response.status_code, 200)
		self.assertTrue('Logout gitlab' in str(response.content))
		self.assertTrue('firstname' in str(response.content))
		self.assertTrue('lastname' in str(response.content))
		self.assertTrue('mail' in str(response.content))

	def test_logout(self):
		self.client.login(username='testuser', password='hello') 
		response = self._ajax('/auth/logout/', {})
		self.assertEquals(response.status_code, 200)
		self.assertTrue('Login with gitlab' in str(response.content))
	

