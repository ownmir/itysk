from django.test import TestCase
from django.contrib.auth.models import User
from django.urls import reverse, resolve
from ..views import forget_password


class ForgetPasswordTests(TestCase):
    def setUp(self):
        url = reverse('tysk:forget-password')
        self.response = self.client.get(url)
        self.user = User.objects.create_user(username='neo@zion.net', email='neo@zion.net', password='mtrxai6ver')
        self.client.login(username='neo@zion.net', password='mtrxai6ver')

    def test_register_view_success_status_code(self):
        self.assertEquals(self.response.status_code, 200)

    def test_register_url_resolves_register_view(self):
        view = resolve('/tysk/users/forget/')
        self.assertEquals(view.func, forget_password)

