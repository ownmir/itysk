from django.test import TestCase
from django.contrib.auth.models import User
from django.urls import reverse, resolve
from ..views import UserChangePassOld
from ..forms import UserChangePasswordForm


class UserChangePasswordOldTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='neo@zion.net', email='neo@zion.net', password='mtrxai6ver')
        self.client.login(username='neo@zion.net', password='mtrxai6ver')
        print('self.user.username', self.user.username, self.user.pk, 'UserChangePasswordOldTests')

    def test_user_change_password_view_success_status_code(self):
        url = reverse('tysk:user-change-pass-old', kwargs={'pk': 1})
        response = self.client.get(url)
        self.assertEquals(response.status_code, 200)

    def test_user_change_password_view_not_found_status_code(self):
        url = reverse('tysk:user-change-pass-old', kwargs={'pk': 9})
        response = self.client.get(url)
        self.assertEquals(response.status_code, 404)

    def test_user_change_password_url_resolves_register_view(self):
        view = resolve('/tysk/users/1/change/pass_old/')
        self.assertEquals(view.func.view_class, UserChangePassOld)

    def test_csrf(self):
        url = reverse('tysk:user-change-pass-old', kwargs={'pk': 1})
        response = self.client.get(url)
        self.assertContains(response, 'csrfmiddlewaretoken')

    def test_contains_form(self):
        url = reverse('tysk:user-change-pass-old', kwargs={'pk': 1})
        response = self.client.get(url)
        form = response.context.get('form_user')
        self.assertIsInstance(form, UserChangePasswordForm)


class SuccessfulUserChangePasswordOldTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='trinity@zion.net', email='trinity@zion.net', password='mtrxai6ver')
        self.client.login(username='trinity@zion.net', password='mtrxai6ver')
        print('self.user.username', self.user.username, self.user.pk, 'SuccessfulUserChangePasswordOldTests')
        self.url = reverse('tysk:user-change-pass-old', kwargs={'pk': 2})
        self.response = self.client.post(self.url, {'old_password': 'mtrxai6ver', 'new_password1': 'alsk182736Dj',
                                                    'new_password2': 'alsk182736Dj'})

    def test_redirection(self):
        self.assertRedirects(self.response, reverse('tysk:login'))


class InvalidUserChangePasswordOldTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='tank@zion.net', email='tank@zion.net', password='mtrxai6ver')
        self.client.login(username='tank@zion.net', password='mtrxai6ver')
        print('self.user.username', self.user.username, self.user.pk, 'InvalidUserChangePasswordOldTests')
        self.url = reverse('tysk:user-change-pass-old', kwargs={'pk': 2})
        self.response = self.client.post(self.url, {'new_password1': 'alsk182736Dj'})

    def test_change_password_status_code(self):
        # невалидная форма должна возвращать ту же страницу
        self.assertEquals(self.response.status_code, 200)

    def test_form_errors(self):
        form_user = self.response.context.get('form_user')
        self.assertTrue(form_user.errors)
