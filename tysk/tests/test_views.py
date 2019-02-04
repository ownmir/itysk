from django.test import TestCase, Client
from django.contrib.auth.models import User
from ..models import Patient, Doctor
from decouple import config


# # користувачі при впровадженні
# class UsersTests(TestCase):
#     fixtures = ['user.json', 'tysk.json']
#
#     def test_exists_setup_users(self):
#         self.assertEquals(User.objects.get(username=config('suser')).username, config('suser'))
#         self.assertEquals(User.objects.get(username=config('test')).username, config('test'))
#         self.assertEquals(User.objects.get(username=config('self')).username, config('self'))
#
#     def test_exists_setup_patient(self):
#         test_user = User.objects.get(username=config('test'))
#         self.assertEqual(Patient.objects.get(user=test_user).user.username, config('test'), 'Нема тестового пацієнта.. Кого рятувати в першу чергу?')
#
#     def test_exists_setup_doctor(self):
#         self_user = User.objects.get(username=config('self'))
#         self.assertEqual(Doctor.objects.get(user=self_user).user.username, config('self'), 'Нема доктора Сам собі(')
#

class PagesTests(TestCase):

    def setUp(self):
        self.client = Client()

    def response_test(self, url='/tysk/'):
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        url_list = ['/tysk/doctors/', '/tysk/mains/', '/tysk/medicaments/', '/tysk/users/', '/tysk/users/',
                    '/tysk/about/', '/tysk/contact/', '/tysk/faq/', '/tysk/patients/']
        for url_txt in url_list:
            response = self.client.get(url_txt)
            self.assertEqual(response.status_code, 200)

    def login_test(self):
        print('The login test is begining...')
        login = self.client.login(username=config('test'), password=config('test_pass'))
        self.assertTrue(login, 'Користувач test login fall')
        # user = User.objects.get(username='config('test'))
        # print(user)
        # force_login = self.client.force_login(user)
        # self.assertTrue(force_login, 'Користувач test force login fall')
        response = self.client.post('/tysk/users/login/?next=/tysk/', {'username': config('test'),
                                                                       'password': config('test_pass')})
        self.assertRedirects(response, '/tysk/', 302, 200)
        response = self.client.get('/accounts/google/login/?method=oauth2&next=/tysk/', follow=True)
        print(response.status_code)
        print(response.redirect_chain)

    def login_superuser(self):
        import logging
        logging.basicConfig(format = u'%(filename)s[LINE:%(lineno)d]# %(levelname)-8s [%(asctime)s]  %(message)s',
                            level=logging.DEBUG)
        logging.info('The login superuser is begining..')
        login = self.client.login(username=config('suser'), password=config('suser_pass'))
        self.assertTrue(login, 'Користувач su login fall')
        logging.debug('debug')
        logging.warning('warning')

#
# page_test = PagesTests()
# page_test.setUp()
# page_test.response_test('/tysk/')
# page_test.response_test('/tysk/doctors/')
# page_test.response_test('/tysk/mains/')
# page_test.response_test('/tysk/medicaments/')
# page_test.response_test('/tysk/users/')
# page_test.response_test('/tysk/about/')
# page_test.response_test('/tysk/contact/')
# page_test.response_test('/tysk/faq/')
# page_test.response_test('/tysk/patients/')
# # page_test.login_test()
# page_test.login_superuser()
#
# # user_test = UserTests()