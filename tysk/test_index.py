from django.test import TestCase, Client


class IndexTests(TestCase):

    def setup(self):
        self.client = Client()

    def response_test(self):
        response = self.client.get('/tysk/')
        print('response.status_code')
        print(response.status_code)
        self.assertEqual(response.status_code, 200)
