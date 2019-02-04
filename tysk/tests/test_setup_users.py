from django.test import TestCase
from django.contrib.auth.models import User
from ..models import Patient, Doctor
from decouple import config


# користувачі при впровадженні
class UsersTests(TestCase):
    fixtures = ['user.json', 'tysk.json']

    def test_exists_setup_users(self):
        self.assertEquals(User.objects.get(username=config('suser')).username, config('suser'))
        self.assertEquals(User.objects.get(username=config('test')).username, config('test'))
        self.assertEquals(User.objects.get(username=config('self')).username, config('self'))

    def test_exists_setup_patient(self):
        test_user = User.objects.get(username=config('test'))
        self.assertEqual(Patient.objects.get(user=test_user).user.username, config('test'), 'Нема тестового пацієнта.. Кого рятувати в першу чергу?')

    def test_exists_setup_doctor(self):
        self_user = User.objects.get(username=config('self'))
        self.assertEqual(Doctor.objects.get(user=self_user).user.username, config('self'), 'Нема доктора Сам собі(')
