from django.test import TestCase
from django.contrib.auth.models import User
from django.urls import reverse, resolve
from ..views import UserResetPass
from ..forms import UserPasswordResetForm
from django.core import mail


class UserResetPasswordTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='neo@zion.net', email='neo@zion.net', password='mtrxai6ver')
        self.client.login(username='neo@zion.net', password='mtrxai6ver')
        print('self.user.username', self.user.username, self.user.pk, 'UserResetPasswordTests')

    def test_user_reset_password_view_success_status_code(self):
        url = reverse('tysk:user-reset-password', kwargs={'username': 'neo@zion.net'})
        response = self.client.get(url)
        self.assertEquals(response.status_code, 200)

    def test_user_reset_password_view_not_found_status_code(self):
        url = reverse('tysk:user-reset-password', kwargs={'username': 'smith@zion.net'})
        response = self.client.get(url)
        self.assertEquals(response.status_code, 404)

    def test_user_reset_password_url_resolves_register_view(self):
        view = resolve('/tysk/users/neo@zion.net/reset/pass/')
        self.assertEquals(view.func.view_class, UserResetPass)

    def test_csrf(self):
        url = reverse('tysk:user-reset-password', kwargs={'username': 'neo@zion.net'})
        response = self.client.get(url)
        self.assertContains(response, 'csrfmiddlewaretoken')

    def test_contains_form(self):
        url = reverse('tysk:user-reset-password', kwargs={'username': 'neo@zion.net'})
        response = self.client.get(url)
        form = response.context.get('form_user')
        self.assertIsInstance(form, UserPasswordResetForm)


class SuccessfulUserResetPasswordTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='trinity@zion.net', email='trinity@zion.net', password='mtrxai6ver')
        self.client.login(username='trinity@zion.net', password='mtrxai6ver')
        print('self.user.username', self.user.username, self.user.pk, 'SuccessfulUserResetPasswordTests')
        self.url = reverse('tysk:user-reset-password', kwargs={'username': 'trinity@zion.net'})
        self.response = self.client.post(self.url, {'username': 'trinity@zion.net', 'email': 'trinity@zion.net'})

    def test_redirection(self):
        self.assertRedirects(self.response, reverse('tysk:user-reset-password-done'))


class InvalidUserResetPasswordTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='tank@zion.net', email='tank@zion.net', password='mtrxai6ver')
        self.client.login(username='tank@zion.net', password='mtrxai6ver')
        # print('self.user.username', self.user.username, self.user.email, 'InvalidUserResetPasswordTests')
        form = UserPasswordResetForm(data={'username': self.user.username, 'email': self.user.email})
        self.url = reverse('tysk:user-reset-password', kwargs={'username': 'tank@zion.net'})
        self.response = self.client.post(self.url, {'form_user': form})

    def test_reset_password_status_code(self):
        # невалидная форма должна возвращать ту же страницу
        self.assertEquals(self.response.status_code, 200)

    def test_form_errors(self):
        form_user = self.response.context.get('form_user')
        self.assertTrue(form_user.errors)


class EmailTest(TestCase):
    def test_send_email(self):
        # Send message.
        mail.send_mail('Subject here', 'Here is the message.',
            'from@example.com', ['to@example.com'],
            fail_silently=False)

        # Test that one message has been sent.
        self.assertEqual(len(mail.outbox), 1)

        # Verify that the subject of the first message is correct.
        self.assertEqual(mail.outbox[0].subject, 'Subject here')