from django.db import models
from django.contrib.auth.models import User, Group
from django.core.exceptions import ObjectDoesNotExist
from django.utils.timezone import now, localtime
from django.core import validators
from django.shortcuts import reverse
from decouple import config


# Власник за замовчуванням - test
def get_default_user():
    try:
        user = User.objects.get(username=config('test'))
    except ObjectDoesNotExist:
        # Немає
        user = User.objects.create_user(config('test'), config('test_email'), config('test_pass'))
        user.first_name = 'В'
        user.last_name = 'Тест паціент'
        user.middle_name = 'В'
        user.is_superuser = False
        user.is_staff = True
        # https://stackoverflow.com/questions/50015204/direct-assignment-to-the-forward-side-of-a-many-to-many-set-is-prohibited-use-e
        user.groups.set(Group.objects.all())
        user.save()
        print('*** test user created in models/get_default_user()! ***')
    return user.pk


# Пацієнти
class Patient(models.Model):
    class Meta:
        verbose_name = 'пацієнт'
        verbose_name_plural = 'пацієнти'

    user = models.OneToOneField(User, verbose_name='користувач', on_delete=models.CASCADE)
    doctors = models.ManyToManyField('Doctor', verbose_name='лікар')
    male = models.BooleanField(verbose_name='стать', default=True)

    def __str__(self):
        return self.user.last_name

    def get_absolute_url(self):
        return reverse('tysk:patient-detail', kwargs={'pk': self.pk})


# Лікарі
class Doctor(models.Model):
    class Meta:
        verbose_name = 'лікар'
        verbose_name_plural = 'лікарі'

    user = models.OneToOneField(User, verbose_name='користувач', on_delete=models.CASCADE)
    patients = models.ManyToManyField(Patient, verbose_name='паціент')

    def __str__(self):
        return self.user.last_name

    def get_absolute_url(self):
        return reverse('tysk:doctor-detail', kwargs={'pk': self.pk})


# Ліки
class Medicament(models.Model):
    class Meta:
        verbose_name = 'ліки'
        verbose_name_plural = 'ліки'

    name = models.CharField(max_length=200, verbose_name='назва, кількість, дозування...')
    owner = models.ForeignKey(User, verbose_name='власник', default=get_default_user, on_delete=models.CASCADE)

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('tysk:medicament-detail', kwargs={'pk': self.pk})


# Головна
class Main(models.Model):
    class Meta:
        verbose_name = 'головна'
        verbose_name_plural = 'головні'

    patient = models.ForeignKey(Patient, verbose_name='пацієнт', on_delete=models.CASCADE)
    doctor = models.ForeignKey(Doctor, verbose_name='лікар', on_delete=models.CASCADE)  # , help_text='Виберіть лікарів, або значення "Я сам"'
    date = models.DateField('дата вимірювання', default=localtime(now()).date())
    time = models.TimeField('час вимірювання', default=localtime(now()).time())
    upper = models.PositiveSmallIntegerField('верхній',
                                             validators=[validators.MinValueValidator(0),
                                                         validators.MaxValueValidator(300)])
    lower = models.PositiveSmallIntegerField('нижній',
                                             validators=[validators.MinValueValidator(0),
                                                         validators.MaxValueValidator(300)])
    pulse = models.PositiveSmallIntegerField('пульс', blank=True,
                                             validators=[validators.MinValueValidator(0),
                                                         validators.MaxValueValidator(300)])
    medicament = models.ForeignKey(Medicament, verbose_name='ліки', on_delete=models.CASCADE)

    # https://djbook.ru/rel1.9/ref/models/fields.html#default
    # Для полей типа ForeignKey, которые ссылаются на объекты модели, значением по умолчанию должно быть значение поля
    # на которое они ссылаются (pk, если не указан to_field), а не объект модели.
    owner = models.ForeignKey(User, verbose_name='власник', default=get_default_user, on_delete=models.CASCADE)

    def get_absolute_url(self):
        return reverse('tysk:main-detail', args=[str(self.pk)])
