from django.test import TestCase
from django.contrib.auth.models import User
from django.urls import reverse, resolve
from ..views import UserDelete


class UserConfirmDeleteTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='neo@zion.net', email='neo@zion.net', password='mtrxai6ver')
        self.client.login(username='neo@zion.net', password='mtrxai6ver')
        print('self.user.username', self.user.username, self.user.pk, 'UserConfirmDeleteTests')

    def test_user_confirm_delete_view_success_status_code(self):
        url = reverse('tysk:user-delete', kwargs={'pk': 1})
        response = self.client.get(url)
        self.assertEquals(response.status_code, 200)

    def test_user_confirm_delete_view_not_found_status_code(self):
        url = reverse('tysk:user-delete', kwargs={'pk': 9})
        response = self.client.get(url)
        self.assertEquals(response.status_code, 404)

    def test_user_confirm_delete_resolves_register_view(self):
        view = resolve('/tysk/users/1/confirm/')
        self.assertEquals(view.func.view_class, UserDelete)

    def test_csrf(self):
        url = reverse('tysk:user-delete', kwargs={'pk': 1})
        response = self.client.get(url)
        self.assertContains(response, 'csrfmiddlewaretoken')


class SuccessfulUserConfirmDeleteTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='trinity@zion.net', email='trinity@zion.net', password='mtrxai6ver')
        self.client.login(username='trinity@zion.net', password='mtrxai6ver')
        print('self.user.username', self.user.username, self.user.pk, 'SuccessfulUserConfirmDeleteTests')
        self.url = reverse('tysk:user-delete', kwargs={'pk': 2})
        self.response = self.client.post(self.url)

    def test_redirection(self):
        self.assertRedirects(self.response, reverse('tysk:index'))


class InvalidUserConfirmDeleteTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='tank@zion.net', email='tank@zion.net', password='mtrxai6ver')
        self.client.login(username='tank@zion.net', password='mtrxai6ver')
        print('self.user.username', self.user.username, self.user.pk, 'InvalidUserChangePasswordTests')
        self.user2 = User.objects.create_user(username='mev@zion.net', email='mev@zion.net', password='mtrxai6ver')
        print('self.user2.username', self.user2.username, self.user2.pk, 'InvalidUserConfirmDeleteTests')
        self.url = reverse('tysk:user-delete', kwargs={'pk': 3})
        self.response = self.client.post(self.url)

    def test_confirm_delete_status_code(self):
        # невалидная форма должна возвращать ту же страницу
        self.assertEquals(self.response.status_code, 200)

    def test_form_errors(self):
        error = self.response.context.get('error_message')
        self.assertTrue(error)
