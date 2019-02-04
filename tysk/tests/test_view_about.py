from django.test import TestCase
from django.urls import reverse, resolve
from ..views import about


class UserAboutTests(TestCase):
    def setUp(self):
        url = reverse('tysk:about')
        self.response = self.client.get(url)

    def test_about_success_status_code(self):
        self.assertEquals(self.response.status_code, 200)

    def test_about_url_resolves_register_view(self):
        view = resolve('/tysk/about/')
        self.assertEquals(view.func, about)
