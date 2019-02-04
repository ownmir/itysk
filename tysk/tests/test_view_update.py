from django.test import TestCase
from django.contrib.auth.models import User
from django.urls import reverse, resolve
from ..views import UserUpdate
from ..forms import UserForm


class UserUpdateTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='neo@zion.net', email='neo@zion.net', password='mtrxai6ver')
        self.client.login(username='neo@zion.net', password='mtrxai6ver')
        print('self.user.username', self.user.username, self.user.pk, 'UserUpdateTests')

    def test_user_update_view_success_status_code(self):
        url = reverse('tysk:user-update', kwargs={'pk': 1})
        response = self.client.get(url)
        self.assertEquals(response.status_code, 200)

    def test_user_update_view_not_found_status_code(self):
        url = reverse('tysk:user-update', kwargs={'pk': 9})
        response = self.client.get(url)
        self.assertEquals(response.status_code, 404)

    def test_user_update_url_resolves_register_view(self):
        view = resolve('/tysk/users/1/update/')
        self.assertEquals(view.func.view_class, UserUpdate)

    def test_csrf(self):
        url = reverse('tysk:user-update', kwargs={'pk': 1})
        response = self.client.get(url)
        self.assertContains(response, 'csrfmiddlewaretoken')

    def test_contains_form(self):
        url = reverse('tysk:user-update', kwargs={'pk': 1})
        response = self.client.get(url)
        form = response.context.get('form_user')
        self.assertIsInstance(form, UserForm)


class SuccessfulUserUpdateTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='trinity@zion.net', email='trinity@zion.net', password='mtrxai6ver')
        self.client.login(username='trinity@zion.net', password='mtrxai6ver')
        print('self.user.username', self.user.username, self.user.pk, 'SuccessfulUserUpdateTests')
        self.url = reverse('tysk:user-update', kwargs={'pk': 2})
        self.response = \
            self.client.post(self.url,
                             {'username': self.user.username, 'first_name': 'Trinity', 'last_name': 'Girlfriend',
                              'email': self.user.email})

    def test_redirection(self):
        self.assertRedirects(self.response, reverse('tysk:index'))


class InvalidUserUpdateTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='tank@zion.net', email='tank@zion.net', password='mtrxai6ver')
        self.client.login(username='tank@zion.net', password='mtrxai6ver')
        print('self.user.username', self.user.username, self.user.pk, 'InvalidUserUpdateTests')
        self.url = reverse('tysk:user-update', kwargs={'pk': 2})
        self.response = \
            self.client.post(self.url,
                             {'username': '', 'first_name': 'Tank', 'last_name': 'Operator',
                              'email': self.user.username})

    def test_update_status_code(self):
        # невалидная форма должна возвращать ту же страницу
        self.assertEquals(self.response.status_code, 200)

    def test_form_errors(self):
        form_user = self.response.context.get('form_user')
        self.assertTrue(form_user.errors)
