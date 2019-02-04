from django.test import TestCase
from django.contrib.auth.models import User
from django.urls import reverse, resolve
from ..views import logout


class UserLogoutTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='neo@zion.net', email='neo@zion.net', password='mtrxai6ver')
        self.client.login(username='neo@zion.net', password='mtrxai6ver')
        url = reverse('tysk:logout')
        self.response = self.client.get(url)

    def test_user_logout_success_status_code(self):
        self.assertEquals(self.response.status_code, 200)

    def test_logout_url_resolves_register_view(self):
        view = resolve('/tysk/users/logout/')
        self.assertEquals(view.func, logout)
