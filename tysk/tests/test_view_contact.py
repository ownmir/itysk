from django.test import TestCase
from django.urls import reverse, resolve
from ..views import contact


class UserContactTests(TestCase):
    def setUp(self):
        url = reverse('tysk:contact')
        self.response = self.client.get(url)

    def test_contact_success_status_code(self):
        self.assertEquals(self.response.status_code, 200)

    def test_contact_url_resolves_register_view(self):
        view = resolve('/tysk/contact/')
        self.assertEquals(view.func, contact)
