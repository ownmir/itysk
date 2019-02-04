from django.test import TestCase
from django.contrib.auth.models import User
from django.urls import reverse, resolve
from ..views import register
from ..forms import RegisterForm
from decouple import config


class RegisterTests(TestCase):
    def setUp(self):
        url = reverse('tysk:register')
        self.response = self.client.get(url)
        # self.user = User.objects.create_user(username='neo', email='neo@zion.net', password='mtrxai6ver')
        # self.client.login(username='neo', password='mtrxai6ver')

    def test_register_view_success_status_code(self):
        self.assertEquals(self.response.status_code, 200)

    def test_register_url_resolves_register_view(self):
        view = resolve('/tysk/users/reg/')
        self.assertEquals(view.func, register)

    def test_csrf(self):
        self.assertContains(self.response, 'csrfmiddlewaretoken')

    def test_contains_form(self):
        form = self.response.context.get('form')
        self.assertIsInstance(form, RegisterForm)

    def test_form_inputs(self):
        self.assertContains(self.response, '<input', 9)
        self.assertContains(self.response, 'type="text"', 2)
        self.assertContains(self.response, 'type="password"', 2)
        self.assertContains(self.response, 'type="radio"', 4)


class SuccessfulRegisterTestsMalePatient(TestCase):
    def setUp(self):
        url = reverse('tysk:register')
        data = {
            'username': 'neo@zion.net',
            'password1': 'mtrxai6ver',
            'password2': 'mtrxai6ver',
            'first_name': 'TheOne',
            'gender': 'male',
            'type_user': 'patient'
        }
        self.response = self.client.post(url, data)
        self.index_url = reverse('tysk:index')

    def test_redirection(self):
        self.assertRedirects(self.response, self.index_url)

    def test_user_creation(self):
        self.assertTrue(User.objects.exists())

    def test_user_authentication(self):
        response = self.client.get(self.index_url)
        user = response.context.get('user')
        self.assertTrue(user.is_authenticated)
    # def test_right_template(self):
    #     self.assertTemplateUsed(self.response, 'tysk/user/patient-created.html')


class SuccessfulRegisterTestsFemalePatient(TestCase):
    def setUp(self):
        url = reverse('tysk:register')
        data = {
            'username': 'neo@zion.net',
            'password1': 'mtrxai6ver',
            'password2': 'mtrxai6ver',
            'first_name': 'TheOne',
            'gender': 'female',
            'type_user': 'patient'
        }
        self.response = self.client.post(url, data)
        self.index_url = reverse('tysk:index')

    def test_redirection(self):
        self.assertRedirects(self.response, self.index_url)

    def test_user_creation(self):
        self.assertTrue(User.objects.exists())

    def test_user_authentication(self):
        response = self.client.get(self.index_url)
        user = response.context.get('user')
        self.assertTrue(user.is_authenticated)


class SuccessfulRegisterTestsMaleDoctor(TestCase):
    def setUp(self):
        url = reverse('tysk:register')
        data = {
            'username': 'neo@zion.net',
            'password1': 'mtrxai6ver',
            'password2': 'mtrxai6ver',
            'first_name': 'TheOne',
            'gender': 'male',
            'type_user': 'doctor'
        }
        self.response = self.client.post(url, data)
        self.index_url = reverse('tysk:index')

    def test_redirection(self):
        self.assertRedirects(self.response, self.index_url)

    def test_user_creation(self):
        self.assertTrue(User.objects.exists())

    def test_user_authentication(self):
        response = self.client.get(self.index_url)
        user = response.context.get('user')
        self.assertTrue(user.is_authenticated)


class SuccessfulRegisterTestsFemaleDoctor(TestCase):
    def setUp(self):
        url = reverse('tysk:register')
        data = {
            'username': 'neo@zion.net',
            'password1': 'mtrxai6ver',
            'password2': 'mtrxai6ver',
            'first_name': 'TheOne',
            'gender': 'female',
            'type_user': 'doctor'
        }
        self.response = self.client.post(url, data)
        self.index_url = reverse('tysk:index')

    def test_redirection(self):
        self.assertRedirects(self.response, self.index_url)

    def test_user_creation(self):
        self.assertTrue(User.objects.exists())

    def test_user_authentication(self):
        response = self.client.get(self.index_url)
        user = response.context.get('user')
        self.assertTrue(user.is_authenticated)


class InvalidRegisterTests(TestCase):
    def setUp(self):
        url = reverse('tysk:register')
        data = {
            'username': '',
            'password1': '',
            'password2': '',
            'first_name': '',
            'gender': 'male',
            'type_user': 'patient'
        }
        self.response = self.client.post(url, data)

    def test_signup_status_code(self):
        self.assertEquals(self.response.status_code, 200)

    def test_form_errors(self):
        form = self.response.context.get('form')
        self.assertTrue(form.errors)

    def test_dont_create_user(self):
        container = User.objects.all()
        print('container', container)
        for u in container:
            print(u.last_name)
        try:
            member = User.objects.get(username=config('suser'))
            self.assertNotIn(member, container)
        except:
            pass
        try:
            member = User.objects.get(username=config('self'))
            self.assertNotIn(member, container)
        except:
            pass
        try:
            member = User.objects.get(username=config('test'))
            self.assertNotIn(member, container)
        except:
            pass


class UserExistsRegisterTests(TestCase):
    def setUp(self):
        url = reverse('tysk:register')
        self.user = User.objects.create_user(username='blind@matrix.net', email='blind@matrix.net', password='mtrxai6ver')
        data = {
            'username': 'blind@matrix.net',
            'password1': 'mtrxai6ver',
            'password2': 'mtrxai6ver',
            'first_name': 'John',
            'gender': 'male',
            'type_user': 'patient'
        }
        self.response = self.client.post(url, data)
        # self.user_exists_url = reverse('tysk/user/user-exists.html')

    def test_right_template(self):
        self.assertIsInstance(self.user, User)
        self.assertTemplateUsed(self.response, 'tysk/user/user-exists.html')
