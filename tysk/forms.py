from django.contrib.auth.forms import UserChangeForm, UserCreationForm, SetPasswordForm, PasswordChangeForm \
    , PasswordResetForm

from . import models
from django import forms
from django.core import mail
from django.contrib.auth.tokens import default_token_generator
from django.template import loader
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode
from django.contrib.sites.shortcuts import get_current_site


def make_error_not_auth():
    raise forms.ValidationError("Зайдіть в свій профіль, будь ласка.")


class UserForm(UserChangeForm):
    def __init__(self, *args, **kwargs):
        super(UserForm, self).__init__(*args, **kwargs)
        del self.fields['password']

    class Meta:
        model = models.User
        fields = ['username', 'first_name', 'last_name', 'email']


class UserSetPasswordForm(SetPasswordForm):
    class Meta:
        model = models.User
        fields = ['password']


class UserChangePasswordForm(PasswordChangeForm):
    class Meta:
        model = models.User
        fields = ['password']


class UserPasswordResetForm(forms.Form):
    template_name = 'tysk/user/user-reset-pass.html'
    email_template_name = 'tysk/user/user-reset-pass-email.html'
    subject_template_name = 'tysk/user/reset_subject.txt'
    from_email = 'noreply@ownsvit.top'
    to_email = ''

    class Meta:
        model = models.User
        fields = ['username', 'email']

    def send_email(self, subject_template_name, email_template_name, context, from_email, to_email,
                   html_email_template_name=None):
        connection = mail.get_connection()
        print('connection', connection)
        if connection.open():
            subject = loader.render_to_string(subject_template_name, context)
            # Email subject *must not* contain newlines
            subject = ''.join(subject.splitlines())
            print('context', context)
            mess = loader.render_to_string(email_template_name, context)
            email1 = mail.EmailMessage(subject, mess, from_email,
                                       [to_email], connection=connection)
            n = email1.send()
            print('n', n)
            connection.close()
        else:
            print('not open(')
            subject = loader.render_to_string(subject_template_name, context)
            # Email subject *must not* contain newlines
            subject = ''.join(subject.splitlines())
            print('context', context)
            mess = loader.render_to_string(email_template_name, context)
            email1 = mail.EmailMessage(subject, mess, from_email,
                                       [to_email], connection=connection)
            n = email1.send()
            print('n', n)

    def save(self, user_object, request):
        print('save')
        username = user_object.username
        print('username', username)
        email = user_object.email
        current_site = get_current_site(request)
        domain = current_site.domain

        context = {'email': email,
                   'uname': urlsafe_base64_encode(force_bytes(username)).decode(),
                   'token': default_token_generator.make_token(user_object),
                   'protocol': 'http',
                   'domain': domain}

        self.send_email(self.subject_template_name, self.email_template_name, context, self.from_email, email)


class TyskUserCreationForm(UserCreationForm):

    class Meta:
        model = models.User
        fields = ['username', 'first_name', 'last_name', 'email', 'groups', 'user_permissions', 'is_staff', 'is_active',
                  'is_superuser']


class RegisterForm(forms.Form):
    GENDER_CHOICES = (
        ('male', 'Чоловіча'),
        ('female', 'Жіноча'),
    )
    TYPE_USER_CHOICES = (
            ('patient', 'Пацієнт'),
            ('doctor', 'Лікар'),
    )
    username = forms.EmailField(label='Електронна пошта')
    password1 = forms.CharField(label='Пароль', help_text='звертайте увагу на мову і регістр', widget=forms.PasswordInput)
    password2 = forms.CharField(label='Підтверження паролю', help_text='', widget=forms.PasswordInput)
    first_name = forms.CharField(label='Ім`я', help_text='ім`я (наприклад - Тарас, Олена)')
    gender = forms.ChoiceField(choices=GENDER_CHOICES, label='Стать', widget=forms.RadioSelect)
    type_user = forms.ChoiceField(choices=TYPE_USER_CHOICES, label='Хто?', widget=forms.RadioSelect)

    def check_passwords_match(self):
        # Check that the two password entries match
        # Визивається в clean
        password1 = self.cleaned_data.get("password1")
        password2 = self.cleaned_data.get("password2")
        if password1 and password2 and password1 != password2:
            # raise forms.ValidationError("Паролі не співпадають")
            return False
        return True

    def clean(self):
        if not self.check_passwords_match():
            super(RegisterForm, self).clean()
            raise forms.ValidationError("Паролі не співпадають")


class IndexForm(forms.Form):
    upper = forms.IntegerField(max_value=300, min_value=0)
    lower = forms.IntegerField(max_value=300, min_value=0)
    pulse = forms.IntegerField(max_value=300, min_value=0)
    email = forms.EmailField()


class MedicamentCreateForm(forms.ModelForm):
    class Meta:
        model = models.Medicament
        fields = ['name', 'owner']
        widgets = {'owner': forms.HiddenInput}


class MedicamentSuperUserCreateForm(forms.ModelForm):
    class Meta:
        model = models.Medicament
        fields = ['name', 'owner']


class MedicamentUpdateForm(forms.ModelForm):
    class Meta:
        model = models.Medicament
        fields = ['name', 'owner']
        widgets = {'owner': forms.HiddenInput}


class MedicamentSuperUserUpdateForm(forms.ModelForm):
    class Meta:
        model = models.Medicament
        fields = ['name', 'owner']


class PatientCreateForm(forms.ModelForm):
    GENDER_CHOICES = (
        (True, 'Чол'),
        (False, 'Жін '),
    )
    male = forms.ChoiceField(choices=GENDER_CHOICES, label='Стать', widget=forms.RadioSelect())

    class Meta:
        model = models.Patient
        fields = ['doctors', 'male', 'user']
        widgets = {'user': forms.HiddenInput}


class PatientSuperUserCreateForm(forms.ModelForm):
    class Meta:
        model = models.Patient
        fields = ['user', 'doctors', 'male']