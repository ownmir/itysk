from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login as auth_login
from django.urls import reverse
from ..models import Patient, Doctor
from decouple import config


class LoginTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='neo', email='neo@zion.net', password='mtrxai6ver')
        self.client.login(username='neo', password='mtrxai6ver')

    def test_login_view_success_status_code(self):
        url = reverse('tysk:login')
        response = self.client.get(url)
        self.assertEquals(response.status_code, 200)

    def test_login_valid_post_data(self):
        url = reverse('tysk:login')
        data = {'username': 'neo', 'password': 'mtrxai6ver'}
        response = self.client.post(url, data)
        self.assertTrue(User.objects.exists())

    def test_login_invalid_post_data(self):
        url = reverse('tysk:login')
        data = {'username': '', 'password': ''}
        response = self.client.post(url, data)
        self.assertEquals(response.status_code, 200)
        authenticate(username=data['username'], password=data['password'])
        error_message = response.context['error_message']
        self.assertEquals(error_message, 'невірний користувач чи пароль, чи користувача заблоковано')

    def test_redirection(self):
        '''
        Test 
        '''
        url = reverse('tysk:login')
        data = {'username': 'neo', 'password': 'mtrxai6ver'}
        response = self.client.post(url, data)
        authenticate(username=data['username'], password=data['password'])
        self.assertRedirects(response, '/tysk/')

    def test_redirection_next_get(self):
        # Test get
        response = self.client.get('/tysk/users/login/?next=/tysk/')
        self.assertTrue(response.status_code, 200)

    def test_redirection_next_post(self):
        # Test post
        data = {'username': 'neo', 'password': 'mtrxai6ver'}
        authenticate(username=data['username'], password=data['password'])
        response_post = self.client.post('/tysk/users/login/?next=/tysk/', data, follow=True)
        url = reverse('tysk:index')
        self.assertRedirects(response_post, url)
