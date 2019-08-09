from django.contrib.auth import authenticate, login as auth_login, \
    logout as auth_logout  # http://stackoverflow.com/questions/39316948/
from django.contrib.auth.models import User, Group
from django.core.exceptions import ObjectDoesNotExist
from django.utils.datastructures import MultiValueDictKeyError
from django.urls import reverse_lazy
from django.shortcuts import render, redirect, get_object_or_404
# typeerror-login-takes-1-positional-argument-but-2-were-given
from django.utils.timezone import now, localtime
from django.views import generic
from django.http import HttpResponseRedirect
from itysk import settings
from decouple import config

from . import forms
from . import models
from .utilities import which_invoked
from django.contrib.auth.views import PasswordResetConfirmView, PasswordResetCompleteView
from django.contrib.auth.tokens import default_token_generator
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode
from django.utils.http import is_safe_url, urlsafe_base64_decode
from django.core.exceptions import ValidationError
from django.utils.decorators import method_decorator
from django.views.decorators.cache import never_cache
from django.views.decorators.debug import sensitive_post_parameters
from django.views.generic.base import TemplateView
from django.views.generic.edit import FormView
from django.template.loader import render_to_string
from django.contrib.sites.models import Site
from django.db.models import Q


def auth_or_create(request):
    context = {}
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(username=username, password=password)
        if user is not None:
            if user.is_active:
                auth_login(request, user)
                # Redirect to a success page.
            else:
                # Return a 'disabled account' error message
                pass
        else:
            # Return an 'invalid login' error message.
            pass
    if not request.user.is_authenticated:
        create_user_self(request)
    return context


def index(request):
    # початкова
    context = {'active': 'index'}
    user = request.user
    if not request.user.is_authenticated:
        create_user_self(request)
        print("create_user_self виконано!")
    if request.method == 'POST':
        main_form = forms.IndexForm(request.POST)
        upper = request.POST['upper']
        lower = request.POST['lower']
        pulse = request.POST['pulse']
        email = request.POST['email']
        context['main_form'] = main_form
        if not request.user.is_authenticated and 'database_save' in main_form.data:
            forms.make_error_not_auth()  # додаємо помилку
        if main_form.is_valid():
            if 'send_email' in main_form.data:
                print('send_email !')
                from django.core import mail
                connection = mail.get_connection()
                if connection.open():
                    there = '\n Поскаржитись на цей лист можна тут www.ownsvit.top/tysk/contact/ '
                        # {'protocol': 'https://', 'domain': Site.objects.get_current(request).domain})
                    subject = 'Тиск. www.ownsvit.top/tysk/. Дата: ' + str(localtime().date()) + ', час ' + str(localtime().time())
                    mess = 'Вітаю! \nЦей лист прийшов Вам з сайту www.ownsvit.top/tysk/ . Верхній тиск: ' + str(upper) + \
                        ', нижній ' + str(lower) + ', пульс ' + str(pulse) + '.\n З повагою, команда Тиск.'
                    email1 = mail.EmailMessage(subject, mess + there, 'postmaster@ownsvit.top',
                                               [email], connection=connection)
                    # email1.attach_alternative(mess + there, 'text/html')
                    email1.send()
                    connection.close()
                    print(':-)')
                return render(request, 'tysk/index.html', context)
            # Створюємо main
            main = models.Main()
            # Шукаємо паціента
            try:
                patient = models.Patient.objects.get(user=user)
            except ObjectDoesNotExist:
                patient = models.Patient()
                patient.user = user
                patient.male = True
                patient.save()
                self_user = User.objects.get(username=config('self'))
                try:
                    self_doctor = models.Doctor.objects.get(user=self_user)
                except ObjectDoesNotExist:
                    self_doctor = models.Doctor()
                    self_doctor.user = self_user
                    self_doctor.save()
                    test_user = User.objects.get(username=config('test'))
                    try:
                        test_patient = models.Patient.objects.get(user=test_user)
                    except ObjectDoesNotExist:
                        test_patient = models.Patient()
                        test_patient.user = test_user
                        test_patient.male = True
                        test_patient.save()
                        print('*** test user created in views/index()! ***')
                        test_patient.doctors.add(self_doctor)
                patient.doctors.add(self_doctor)
            main.patient = patient
            # Шукаємо доктора
            if not patient.doctors.exists():
                self_user = User.objects.get(username=config('self'))
                self_doctor = models.Doctor.objects.get(user=self_user)
                patient.doctors.add(self_doctor)
            doctor = patient.doctors.all()[0]
            main.doctor = doctor
            main.upper = main_form.cleaned_data.get('upper')
            main.lower = main_form.cleaned_data.get('lower')
            main.pulse = main_form.cleaned_data.get('pulse')
            # main.date default - current
            # main.time default - current
            # Шукаємо ліки
            try:
                medicament = models.Medicament.objects.get(name='Не приймали')
            except ObjectDoesNotExist:
                medicament = models.Medicament()
                medicament.name = 'Не приймали'
                medicament.save()
                print('Ліки створено!')
            main.medicament = medicament
            main.owner = user
            main.save()
            # return HttpResponse('First go...')
            return redirect(main)
        else:
            main_form = forms.IndexForm(request.POST)
            print(request.POST)
            context['main_form'] = main_form
            context['upper'] = upper
            context['lower'] = lower
            context['pulse'] = pulse
            context['email'] = email
        return render(request, 'tysk/index.html', context)
    else:
        if user.is_authenticated:
            main_form = forms.IndexForm(initial={'email': user.email, 'pulse': '60'})
            if user.is_superuser:
                context['is_superuser'] = 'is_superuser'
                main_list = models.Main.objects.order_by('-date', '-time')[:5]
            else:
                main_list = models.Main.objects.filter(owner=user)
                """
                try:
                    # чи пацієнт
                    current_patient = models.Patient.objects.get(user=request.user)
                    main_list = models.Main.objects.filter(patient=current_patient).order_by('-date', '-time')[:5]
                except ObjectDoesNotExist:
                    # чи доктор
                    current_doctor = models.Doctor.objects.get(user=request.user)
                    main_list = models.Main.objects.filter(doctor=current_doctor).order_by('-date', '-time')[:5]
                """
        else:
            main_form = forms.IndexForm(initial={'pulse': '60'})
            main_list = []
        context['main_form'] = main_form
        context['main_list'] = main_list
        return render(request, 'tysk/index.html', context)


def create_user_self(request):
    # створення користувача "Суперюзер" при впровадженні
    try:
        user = User.objects.get(username=config('suser'))
    except ObjectDoesNotExist:
        # Немає
        user = User.objects.create_superuser(config('suser'), config('suser_email'), config('suser_pass'))
        user.first_name = 'В'
        user.last_name = 'Суперюзер'
        user.middle_name = 'В'
        user.groups.set(Group.objects.all())
        user.save()
    # створення користувача "Я сам лікар)" при впровадженні
    try:
        user = User.objects.get(username=config('self'))
    except ObjectDoesNotExist:
        # Немає
        user = User.objects.create_user(config('self'), config('self_email'), config('self_pass'))
        user.first_name = 'В'
        user.last_name = 'Я сам лікар)'
        user.middle_name = 'В'
        user.is_superuser = False
        user.is_staff = True
        user.groups.set(Group.objects.all())
        user.save()
    # створення користувача "Тест паціент" при впровадженні
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
        user.groups.set(Group.objects.all())
        user.save()
        print('*** test user created in views/create_user_self()! ***')
    try:
        medicament = models.Medicament.objects.get(name="Не приймали")
    except ObjectDoesNotExist:
        medicament = models.Medicament.objects.create(name="Не приймали")
        medicament.save()
        print("Стандартний медикамент 'Не приймали' створено!")
    return


def login(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(username=username, password=password)
        if user is not None:
            auth_login(request, user)
            # Redirect to a success page.
            request.method = 'GET'
            try:
                next_page = request.GET['next']
                print('next_page', next_page)
                return redirect(next_page)
            except MultiValueDictKeyError:
                print('except')
                return redirect('/tysk/')
        else:
            # Return an 'invalid login' error message.
            print('invalid login or not active')
            return render(request, 'tysk/user/user-login.html',
                          {'error_message': 'невірний користувач чи пароль, чи користувача заблоковано'})
    else:
        return render(request, 'tysk/user/user-login.html')


def register(request):
    if request.method == 'POST':
        register_form = forms.RegisterForm(request.POST)
        username = request.POST['username']
        password1 = request.POST['password1']
        password2 = request.POST['password2']
        first_name = request.POST['first_name']
        gender = request.POST['gender']
        print('gender')
        print(gender)
        type_user = request.POST['type_user']
        print('type_user')
        print(type_user)
        if register_form.is_valid():
            try:
                user = User.objects.get(username=username)
                # DONE: Make the page "user exists"
                # return HttpResponse('Такий користувач вже існує!')
                return render(request, 'tysk/user/user-exists.html')
            except ObjectDoesNotExist:
                # немає
                user = User.objects.create_user(username, username, password1)
                user.first_name = first_name
                user.last_name = first_name
                user.middle_name = first_name
                user.is_superuser = False
                user.is_staff = True
                user.groups.set(Group.objects.all())
                user.save()
                # user - пользователь, который регистрируется
                # self_user - экземпляр User
                # test_user - экземпляр User
                # self_doctor - в поле user - self_user, в МногоеКоМногим patients добавлено test_patient
                # test_patient - в поле user - test_user, в МногоеКоМногим doctors добавлено self_doctor
                # 1) готовим self_user
                try:
                    self_user = User.objects.get(username=config('self'))
                except ObjectDoesNotExist:  # Немає
                    self_user = User.objects.create_user(config('self'), config('self_email'), config('self_pass'))
                    self_user.first_name = 'В'
                    self_user.last_name = 'Я сам лікар)'
                    self_user.middle_name = 'В'
                    self_user.is_superuser = False
                    self_user.is_staff = True
                    self_user.groups.set(Group.objects.all())
                    self_user.save()
                # 2) готовим test_user
                try:
                    test_user = User.objects.get(username=config('test'))
                    print('test user exists!')
                except ObjectDoesNotExist:  # Немає
                    test_user = User.objects.create_user(config('test'), config('test_email'), config('test_pass'))
                    test_user.first_name = 'В'
                    test_user.last_name = 'Тест паціент'
                    test_user.middle_name = 'В'
                    test_user.is_superuser = False
                    test_user.is_staff = True
                    test_user.groups.set(Group.objects.all())
                    test_user.save()
                    print('*** test user created in views/register()! ***')
                # 3) готовим self_doctor
                try:
                    self_doctor = models.Doctor.objects.get(user=self_user)
                except ObjectDoesNotExist:
                    self_doctor = models.Doctor()
                    self_doctor.user = self_user
                    self_doctor.save()
                    # self_doctor.patients.add(test_patient) (пациента еще нет)
                # 4) готовим test_patient
                # prepare_test_patient(models.Patient, test_user, self_doctor, )
                try:
                    test_patient = models.Patient.objects.get(user=test_user)
                except ObjectDoesNotExist:
                    test_patient = models.Patient()
                    test_patient.user = test_user
                    test_patient.male = True
                    test_patient.save()
                    test_patient.doctors.add(self_doctor)  # обязательно после save() (Exception Type:
                    # RelatedObjectDoesNotExistException Value: )
                    self_doctor.patients.add(test_patient)
                if type_user == 'patient':
                    try:
                        patient = models.Patient.objects.get(user=user)
                    except ObjectDoesNotExist:
                        patient = models.Patient()
                        patient.user = user
                        patient.male = (gender == 'male')  # True, если gender - мужской
                        patient.save()
                        patient.doctors.add(self_doctor)
                    user = authenticate(username=username, password=password1)
                    if user is not None:
                        auth_login(request, user)
                        # Redirect to a success page.
                        request.method = 'GET'
                        try:
                            next_page = request.GET['next']
                            print('next_page', next_page)
                            return redirect(next_page)
                        except MultiValueDictKeyError:
                            print('except')
                            return redirect('/tysk/')
                    # return render(request, 'tysk/user/patient-created.html')
                else:  # type_user == 'doctor'
                    try:
                        doctor = models.Doctor.objects.get(user=user)
                    except ObjectDoesNotExist:
                        doctor = models.Doctor()
                        doctor.user = user
                        doctor.save()
                        doctor.patients.add(test_patient)
                    user = authenticate(username=username, password=password1)
                    if user is not None:
                        auth_login(request, user)
                        # Redirect to a success page.
                        request.method = 'GET'
                        try:
                            next_page = request.GET['next']
                            print('next_page', next_page)
                            return redirect(next_page)
                        except MultiValueDictKeyError:
                            print('except')
                            return redirect('/tysk/')
                    # return HttpResponse('Доктора створено!')
                    # return render(request, 'tysk/user/doctor-created.html')
        else:
            print('not valid')
            print(register_form.errors)
        return render(request, 'tysk/user/user-register.html', {'form': register_form})
    else:
        register_form = forms.RegisterForm()
        return render(request, 'tysk/user/user-register.html', {'form': register_form})


def forget_password(request):
    return render(request, 'tysk/user/user-forget-pass.html')


class UsersList(generic.ListView):
    model = User
    template_name = 'tysk/user/users-list.html'


class UserDetail(generic.DetailView):
    model = User
    template_name = 'tysk/user/user-detail.html'


# class UserCreate(generic.CreateView):
#     model = User
#     template_name = 'tysk/user/user-create.html'
#     fields = ['username', 'first_name', 'last_name', 'email', 'groups', 'user_permissions', 'is_staff', 'is_active',
#               'is_superuser']
#
#     def get(self, request, *args, **kwargs):
#         # user_object = User.objects.get(id=kwargs['pk'])
#         form_user = forms.TyskUserCreationForm()
#         return render(self.request, self.template_name, {'form_user': form_user})
#
#     def post(self, request, *args, **kwargs):
#         user_object = User()
#         form_user = forms.TyskUserCreationForm(request.POST, instance=user_object)
#         if form_user.is_valid():
#             form_user.save()
#             context = {}
#             context['user_list'] = User.objects.all()
#             print(context)
#             return render(request, 'tysk/user/users-list.html', context)
#         else:
#             return render(request, self.template_name, {'form_user': form_user})
#
#
class UserUpdate(generic.UpdateView):
    model = User
    template_name = 'tysk/user/user-update.html'
    fields = ['username', 'first_name', 'last_name', 'email']

    def get(self, request, *args, **kwargs):
        user_object = get_object_or_404(User, id=kwargs['pk'])
        form_user = forms.UserForm(instance=user_object)
        return render(self.request, self.template_name, {'form_user': form_user})

    def post(self, request, *args, **kwargs):
        user_object = get_object_or_404(User, id=kwargs['pk'])
        form_user = forms.UserForm(request.POST, instance=user_object)
        if form_user.is_valid():
            form_user.save()
            return redirect('/tysk/')
        else:
            print('not valid', user_object.username)
            print(form_user.errors)
            return render(request, self.template_name, {'form_user': form_user})


class UserChangePass(generic.UpdateView):
    model = User
    template_name = 'tysk/user/user-change-pass.html'
    fields = ['password']

    def get(self, request, *args, **kwargs):
        user_object = get_object_or_404(User, id=kwargs['pk'])
        form_user = forms.UserSetPasswordForm(user_object)
        return render(self.request, self.template_name, {'form_user': form_user})

    def post(self, request, *args, **kwargs):
        user_object = get_object_or_404(User, id=kwargs['pk'])
        form_user = forms.UserSetPasswordForm(user_object, request.POST)
        if form_user.is_valid():
            form_user.save()
            return redirect('/tysk/users/login/')
        else:
            return render(request, self.template_name, {'form_user': form_user})


class UserChangePassOld(generic.UpdateView):
    model = User
    template_name = 'tysk/user/user-change-pass-old.html'
    fields = ['password']

    def get(self, request, *args, **kwargs):
        user_object = get_object_or_404(User, id=kwargs['pk'])
        form_user = forms.UserChangePasswordForm(user_object)
        return render(self.request, self.template_name, {'form_user': form_user})

    def post(self, request, *args, **kwargs):
        user_object = get_object_or_404(User, id=kwargs['pk'])
        form_user = forms.UserChangePasswordForm(user_object, request.POST)
        if form_user.is_valid():
            form_user.save()
            return redirect('/tysk/users/login/')
        else:
            return render(request, self.template_name, {'form_user': form_user})


class UserDelete(generic.DeleteView):
    model = User
    template_name = 'tysk/user/user-confirm-delete.html'
    success_url = reverse_lazy('tysk:index')

    def post(self, request, *args, **kwargs):
        user_id = kwargs['pk']
        user_object = get_object_or_404(User, id=user_id)
        if request.user.id == int(user_id):
            user_object.delete()
            return redirect('/tysk/')
        else:
            return render(request, self.template_name, {'error_message': 'Видалити можна тільки користувача на сайті!'})


def logout(request):
    auth_logout(request)
    return render(request, 'tysk/index.html')


def about(request):
    context = {'active': 'about'}
    context.update(auth_or_create(request))
    return render(request, 'tysk/about.html', context)


def contact(request):
    context = {'active': 'contact'}
    # context.update(auth_or_create(request))
    if request.method == 'POST':
        contact_form = forms.ContactForm(request.POST)
        name = request.POST['name']
        email = request.POST['email']
        message = request.POST['message']
        if contact_form.is_valid():
            name = contact_form.cleaned_data['name']
            email = contact_form.cleaned_data['email']
            message = contact_form.cleaned_data['message']
            from django.core import mail
            connection = mail.get_connection()
            if connection.open():
                subject = 'Тиск. Форма зворотнього зв`язку. Дата: ' + str(localtime().date()) + ', час ' + str(
                    localtime().time())
                mess = 'В формі зворотнього зв`язку з сайту www.ownsvit.top/tysk/ . Користувач з електронної поштою: ' \
                       + email + ' ' + name + ', повідомив наступне : ' + message + '.\n З повагою, команда Тиск.'
                email1 = mail.EmailMessage(subject, mess, 'postmaster@ownsvit.top',
                                           ['ownsvit@ukr.net'], connection=connection)
                # email1.attach_alternative(mess + there, 'text/html')
                email1.send()
                connection.close()
                print(':-)')
            else:
                pass
        else:
            contact_form = forms.ContactForm(request.POST)
            context.update({'contact_form': contact_form, 'name': name, 'email': email, 'message': message})
    else:
        contact_form = forms.ContactForm()
    context.update({'contact_form': contact_form})
    return render(request, 'tysk/contact.html', context)


def faq(request):
    context = {'active': 'faq'}
    context.update(auth_or_create(request))
    return render(request, 'tysk/faq.html', context)


class UserResetPass(generic.UpdateView):
    model = User
    token_generator = default_token_generator

    def get(self, request, *args, **kwargs):
        user_object = get_object_or_404(User, username=kwargs['username'])
        form_user = forms.UserPasswordResetForm(initial={'username': user_object.username, 'email': user_object.email})

        return render(self.request, form_user.template_name, {'form_user': form_user}, )

    def post(self, request, *args, **kwargs):
        # print('request.POST.username', request.POST.username)
        user_object = get_object_or_404(User, username=kwargs['username'])
        form_user = forms.UserPasswordResetForm(request.POST)
        if form_user.is_valid():
            print('self.cleaned_data', form_user.cleaned_data)
            form_user.save(user_object, request)
            # form_user.send_email(from_email='admin@localhost', to_email=user_object.email,
            #                      subject_template_name='tysk/user/reset_subject.txt',
            #                      email_template_name='tysk/user/user-reset-pass-email.html',
            #                      context={'username': user_object.username})
            # form_user.send_email(from_email=form_user.from_email, to_email=[user_object.email],
            #                      subject_template_name=form_user.subject_template_name,
            #                      email_template_name=form_user.email_template_name,
            #                      context={'username': user_object.username})
            return redirect('/tysk/users/reset/done/')
        else:
            return render(request, self.template_name, {'form_user': form_user})


class PasswordContextMixin:
    extra_context = None

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({
            'title': self.title,
            **(self.extra_context or {})
        })
        return context


class UserPassResetDoneView(PasswordContextMixin, TemplateView):
    template_name = 'tysk/user/user-reset-pass-done.html'
    title = 'Тиск - Email відправлено'


INTERNAL_RESET_URL_TOKEN = 'set-password'
INTERNAL_RESET_SESSION_TOKEN = '_password_reset_token'


class UserPasswordResetConfirmView(PasswordContextMixin, TemplateView):
    model = User
    form_class = forms.UserSetPasswordForm
    post_reset_login = False
    post_reset_login_backend = None
    success_url = reverse_lazy('tysk/user/user-reset-password-complete')
    template_name = 'tysk/user/user-reset-pass-confirm.html'
    title = 'Введіть новий пароль'
    token_generator = default_token_generator

    @method_decorator(sensitive_post_parameters())
    @method_decorator(never_cache)
    def dispatch(self, *args, **kwargs):
        assert 'unameb64' in kwargs and 'token' in kwargs
        print('kwargs dispatch', kwargs)
        self.validlink = False
        self.user = self.get_user(kwargs['unameb64'])
        if self.user is not None:
            token = kwargs['token']
            if token == INTERNAL_RESET_URL_TOKEN:
                session_token = self.request.session.get(INTERNAL_RESET_SESSION_TOKEN)
                if self.token_generator.check_token(self.user, session_token):
                    # If the token is valid, display the password reset form.
                    self.validlink = True
                    return super().dispatch(*args, **kwargs)
            else:
                if self.token_generator.check_token(self.user, token):
                    # Store the token in the session and redirect to the
                    # password reset form at a URL without the token. That
                    # avoids the possibility of leaking the token in the
                    # HTTP Referer header.
                    self.request.session[INTERNAL_RESET_SESSION_TOKEN] = token
                    redirect_url = self.request.path.replace(token, INTERNAL_RESET_URL_TOKEN)
                    return HttpResponseRedirect(redirect_url)
        return self.render_to_response(self.get_context_data())

    def get_user(self, unameb64):
        print('get_user')
        print('unameb64', unameb64)
        try:
            # urlsafe_base64_decode() decodes to bytestring
            usernamed = urlsafe_base64_decode(unameb64).decode()
            user = self.model._default_manager.get(username=usernamed)
        except (TypeError, ValueError, OverflowError, self.model.DoesNotExist, ValidationError):
            user = None
        return user

    def get_form_kwargs(self):
        print('get_form_kwargs')
        kwargs = super().get_form_kwargs()
        print('kwargs get_form_kwargs', kwargs)

    def form_valid(self, form):
        print('form_valid')
        user = form.save()
        print('user', user)
        del self.request.session[INTERNAL_RESET_SESSION_TOKEN]
        if self.post_reset_login:
            auth_login(self.request, user, self.post_reset_login_backend)
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        print('kwargs get_context_data', kwargs)
        context = super().get_context_data(**kwargs)
        if self.validlink:
            context['validlink'] = True
        else:
            context.update({
                'form': None,
                'title': 'Пароль не скинуто',
                'validlink': False,
            })
        return context


class UserPasswordResetCompleteView(PasswordResetCompleteView):
    model = User
    template_name = 'tysk/user/user-reset-pass-complete.html'


class PatientsList(generic.ListView):
    model = models.Patient
    template_name = 'tysk/patient/patients-list.html'

    def get_context_data(self, **kwargs):
        context = super(PatientsList, self).get_context_data(**kwargs)
        context['active'] = 'patients-list'
        context['is_authenticated'] = self.request.user.is_authenticated
        return context

    def get_queryset(self):
        if not self.request.user.is_authenticated:
            return
        qs = super(PatientsList, self).get_queryset()
        if self.request.user.is_superuser:
            return qs
        qs = qs.filter(Q(user=self.request.user) | Q(doctors__user=self.request.user))
        return qs


class PatientDetail(generic.DetailView):
    model = models.Patient
    template_name = 'tysk/patient/patient-detail.html'

    def get_context_data(self, **kwargs):
        context = super(PatientDetail, self).get_context_data(**kwargs)
        context['active'] = 'patient-detail'
        context['is_authenticated'] = self.request.user.is_authenticated
        return context


class DoctorsList(generic.ListView):
    model = models.Doctor
    template_name = 'tysk/doctor/doctors-list.html'
    # is_doctor = False

    def get_context_data(self, **kwargs):
        context = super(DoctorsList, self).get_context_data(**kwargs)
        context['active'] = 'doctors-list'
        context['is_authenticated'] = self.request.user.is_authenticated
        # self.is_doctor = models.Doctor.objects.filter(user=self.request.user).exists()
        # context['is_doctor'] = self.is_doctor
        return context

    def get_queryset(self):
        if not self.request.user.is_authenticated:
            return
        qs = super(DoctorsList, self).get_queryset()
        if self.request.user.is_superuser:
            return qs
        # qs = qs.filter(user=self.request.user)
        qs = qs.exclude(patient__user__username=config('self'))
        return qs


class DoctorDetail(generic.DetailView):
    model = models.Doctor
    template_name = 'tysk/doctor/doctor-detail.html'

    def get_context_data(self, **kwargs):
        context = super(DoctorDetail, self).get_context_data(**kwargs)
        context['active'] = 'doctor-detail'
        context['is_authenticated'] = self.request.user.is_authenticated
        return context


class MainsList(generic.ListView):
    model = models.Main
    template_name = 'tysk/main/mains-list.html'

    def get_context_data(self, **kwargs):
        context = super(MainsList, self).get_context_data(**kwargs)
        context['active'] = 'mains-list'
        return context

    def get_queryset(self):
        if not self.request.user.is_authenticated:
            return
        qs = super(MainsList, self).get_queryset()
        if self.request.user.is_superuser:
            return qs
        qs = qs.filter(Q(patient__user=self.request.user) | Q(doctor__user=self.request.user) | Q(owner=self.request.user))
        return qs


class MainDetail(generic.DetailView):
    model = models.Main
    template_name = 'tysk/main/main-detail.html'

    def get_context_data(self, **kwargs):
        context = super(MainDetail, self).get_context_data(**kwargs)
        context['active'] = 'main-detail'
        return context


class MainCreate(generic.CreateView):
    model = models.Main
    fields = ['patient', 'doctor', 'date', 'time', 'upper', 'lower', 'pulse', 'medicament']
    template_name = 'tysk/form.html'

    def get_context_data(self, **kwargs):
        context = super(MainCreate, self).get_context_data(**kwargs)
        context['active'] = 'main-add'
        context['model_title'] = 'Головна'
        context['title'] = 'Додавання'
        context['submit'] = 'Додати'
        return context

    def get_queryset(self):
        if not self.request.user.is_authenticated:
            return
        qs = super(MainCreate, self).get_queryset()
        if self.request.user.is_superuser:
            self.fields = ['patient', 'doctor', 'date', 'time', 'upper', 'lower', 'pulse', 'medicament', 'owner']
            print('self.fields')
            print(self.fields)
            return qs
        return qs.filter(owner=self.request.user)


class MainUpdate(generic.UpdateView):
    model = models.Main
    # fields = ['patient', 'doctor', 'date', 'time', 'upper', 'lower', 'pulse', 'medicament', 'owner']
    fields = ['patient', 'doctor', 'date', 'time', 'upper', 'lower', 'pulse', 'medicament']
    template_name = 'tysk/form.html'

    def get_context_data(self, **kwargs):
        context = super(MainUpdate, self).get_context_data(**kwargs)
        context['active'] = 'main-update'
        context['model_title'] = 'Головна'
        context['title'] = 'Зміна'
        context['submit'] = 'Змінити'
        return context

    def get_queryset(self):
        if not self.request.user.is_authenticated:
            return
        qs = super(MainUpdate, self).get_queryset()
        if self.request.user.is_superuser:
            self.fields = ['patient', 'doctor', 'date', 'time', 'upper', 'lower', 'pulse', 'medicament', 'owner']
            return qs
        return qs.filter(owner=self.request.user)


class MainDelete(generic.DeleteView):
    model = models.Main
    template_name = 'tysk/confirm-delete.html'
    success_url = reverse_lazy('tysk:mains-list')

    def get_context_data(self, **kwargs):
        context = super(MainDelete, self).get_context_data(**kwargs)
        context['active'] = 'main-confirm-delete'
        context['model_title'] = 'Головна'
        context['title'] = 'Видалення'
        context['submit'] = 'Видалити'
        return context


class MedicamentsList(generic.ListView):
    model = models.Medicament
    template_name = 'tysk/medicament/medicaments-list.html'

    def get_context_data(self, **kwargs):
        context = super(MedicamentsList, self).get_context_data(**kwargs)
        context['active'] = 'medicament-list'
        return context

    def get_queryset(self):
        if not self.request.user.is_authenticated:
            return
        qs = super(MedicamentsList, self).get_queryset()
        if self.request.user.is_superuser:
            return qs
        qs = qs.filter(Q(owner=self.request.user) | Q(name='Не приймали'))
        return qs


class MedicamentDetail(generic.DetailView):
    model = models.Medicament
    template_name = 'tysk/medicament/medicament-detail.html'

    def get_context_data(self, **kwargs):
        context = super(MedicamentDetail, self).get_context_data(**kwargs)
        context['active'] = 'medicament-detail'
        return context


class MedicamentCreate(generic.CreateView):
    model = models.Medicament
    template_name = 'tysk/form.html'
    form_class = forms.MedicamentCreateForm

    def get(self, request, *args, **kwargs):
        if not self.request.user.is_authenticated:
            return index(request)
        if self.request.user.is_superuser:
            self.form_class = forms.MedicamentSuperUserCreateForm
            print('self.form_class')
            print(self.form_class)
        form = self.form_class(initial={'owner': self.request.user})
        context = {}
        context['active'] = 'medicament-add'
        context['model_title'] = 'Ліки'
        context['title'] = 'Додавання'
        context['submit'] = 'Додати'
        context['form'] = form
        return render(request, self.template_name, context)

    def post(self, request, *args, **kwargs):
        if not self.request.user.is_authenticated:
            return index(request)
        if request.POST["name"] == 'Не приймали':
            if settings.DEBUG == True:
                from django.forms import ValidationError
                raise ValidationError("Не можна додати стандартне значення.")
            else:
                to_user = {}
                to_user['active'] = 'medicament-add'
                to_user['model_title'] = 'Ліки'
                to_user['title'] = 'Додавання'
                to_user['submit'] = 'Додати'
                to_user['e500'] = 'Не можна додати стандартне значення.'
                return render(request, 'tysk/500.html', to_user)
                # return  HttpResponse('<h1>Помилка:</h1><h2>Не можна додати стандартне значення.</h2>')
        if self.request.user.is_superuser:
            self.form_class = forms.MedicamentSuperUserCreateForm
        medicament_object = self.model()
        form = self.form_class(request.POST, instance=medicament_object)
        context = {}
        context['active'] = 'medicament-add'
        context['model_title'] = 'Ліки'
        context['title'] = 'Додавання'
        context['submit'] = 'Додати'
        context['form'] = form
        if form.is_valid():
            form.save()
            context = {}
            context['active'] = 'medicament-list'
            if self.request.user.is_superuser:
                medicament_list = self.model.objects.all()
            else:
                medicament_list = self.model.objects.filter(owner=self.request.user)
            context['medicament_list'] = medicament_list
            return render(request, 'tysk/medicament/medicaments-list.html', context)
        return render(request, self.template_name, context)

    # def form_valid(self, form):
    #     if self.request.user.is_authenticated:
    #         form.instance.owner = self.request.user
    #         form.save()
    #     return super(MedicamentCreate, self).form_valid(form)


class MedicamentUpdate(generic.UpdateView):
    model = models.Medicament
    # За замовченням
    form_class = forms.MedicamentUpdateForm
    template_name = 'tysk/form.html'

    # def get_context_data(self, **kwargs):
    #     context = super(MedicamentUpdate, self).get_context_data(**kwargs)
    #     context['active'] = 'medicament-update'
    #     context['model_title'] = 'Ліки'
    #     context['title'] = 'Зміна'
    #     context['submit'] = 'Змінити'
    #     return context
    #
    # def get_queryset(self):
    #     qs = super(MedicamentUpdate, self).get_queryset()
    #     if self.request.user.is_superuser:
    #         self.fields = ['name', 'owner']
    #         return qs
    #     return qs.filter(owner=self.request.user)

    def get(self, request, *args, **kwargs):
        if not self.request.user.is_authenticated:
            return index(request)
        if self.request.user.is_superuser:
            self.form_class = forms.MedicamentSuperUserUpdateForm
        medicament = models.Medicament.objects.get(pk=kwargs['pk'])
        form = self.form_class(initial={'owner': self.request.user}, instance=medicament)
        context = {}
        context['active'] = 'medicament-update'
        context['model_title'] = 'Ліки'
        context['title'] = 'Зміна'
        context['submit'] = 'Змінити'
        context['form'] = form
        return render(request, self.template_name, context)


class MedicamentDelete(generic.DeleteView):
    model = models.Medicament
    template_name = 'tysk/confirm-delete.html'
    success_url = reverse_lazy('tysk:medicament-list')

    def get_context_data(self, **kwargs):
        context = super(MedicamentDelete, self).get_context_data(**kwargs)
        context['active'] = 'medicament-confirm-delete'
        context['model_title'] = 'Ліки'
        context['title'] = 'Видалення'
        context['submit'] = 'Видалити'
        return context


class PatientUpdate(generic.UpdateView):
    model = models.Patient
    # fields = ['user', 'doctors', 'male']
    template_name = 'tysk/form.html'
    form_class = forms.PatientUpdateForm

    @method_decorator(which_invoked)
    def get_context_data(self, **kwargs):
        context = super(PatientUpdate, self).get_context_data(**kwargs)
        context['active'] = 'patient-update'
        context['model_title'] = 'Пацієнт'
        context['title'] = 'Зміна'
        context['submit'] = 'Змінити'
        return context

    @method_decorator(which_invoked)
    def get(self, request, *args, **kwargs):
        if not self.request.user.is_authenticated:
            return index(request)
        if self.request.user.is_superuser:
            self.form_class = forms.PatientSuperUserUpdateForm
            print('self.form_class (суперюзер)', self.form_class)
        self.object = self.get_object()
        return render(request, self.template_name, self.get_context_data(context={}))
        # HttpResponseRedirect('/tysk/patients/')

    def post(self, request, *args, **kwargs):
        if not self.request.user.is_authenticated:
            return index(request)
        if self.request.user.is_superuser:
            self.form_class = forms.PatientSuperUserUpdateForm
        self.object = self.get_object()
        context = self.get_context_data(context={})
        # patient_object = self.get_object()
        # gender = request.POST['male']
        form = self.form_class(self.request.POST, instance=self.object)
        context['form'] = form
        if form.is_valid():
            form.save()
            context = {}
            context['active'] = 'patient-update'
            context['is_authenticated'] = self.request.user.is_authenticated
            if self.request.user.is_superuser:
                patient_list = self.model.objects.all()
            else:
                patient_list = self.model.objects.filter(user=self.request.user)
            context['patient_list'] = patient_list
            return render(request, 'tysk/patient/patients-list.html', context)
        else:
            print(form.errors)
        return render(request, self.template_name, context)


class PatientDelete(generic.DeleteView):
    model = models.Patient
    template_name = 'tysk/confirm-delete.html'
    success_url = reverse_lazy('tysk:patients-list')

    def get_context_data(self, **kwargs):
        context = super(PatientDelete, self).get_context_data(**kwargs)
        context['active'] = 'patient-confirm-delete'
        context['model_title'] = 'Пацієнт'
        context['title'] = 'Видалення'
        context['submit'] = 'Видалити'
        return context


"""
def code(request):
    context = {'model_class': 'Doctor', 'model_small': 'doctor', 'model_title': 'Лікар', 
    'fields_list': "['user', 'patients']"}
    return render(request, 'tysk/Code/code.gen', context)
"""


def code(request):
    context = {'model_class': 'Main', 'model_small': 'main', 'model_title': 'Головна',
               'fields_list': "['patient', 'doctor', 'date', 'time', 'upper', 'lower', 'pulse', 'medicament']"}
    return render(request, 'tysk/Code/code.gen', context)


class DoctorUpdate(generic.UpdateView):
    model = models.Doctor
    form_class = forms.DoctorUpdateForm
    template_name = 'tysk/form.html'

    def get_context_data(self, **kwargs):
        context = super(DoctorUpdate, self).get_context_data(**kwargs)
        context['active'] = 'doctor-update'
        context['model_title'] = 'Лікар'
        context['title'] = 'Зміна'
        context['submit'] = 'Змінити'
        return context

    def get(self, request, *args, **kwargs):
        print("get")
        if not self.request.user.is_authenticated:
            return index(request)
        if self.request.user.is_superuser:
            self.form_class = forms.DoctorSuperUserUpdateForm
        self.object = self.get_object()
        return render(request, self.template_name, self.get_context_data(context={}))


class DoctorDelete(generic.DeleteView):
    model = models.Doctor
    template_name = 'tysk/confirm-delete.html'
    success_url = reverse_lazy('tysk:doctor-list')

    def get_context_data(self, **kwargs):
        context = super(DoctorDelete, self).get_context_data(**kwargs)
        context['active'] = 'doctor-confirm-delete'
        context['model_title'] = 'Лікар'
        context['title'] = 'Видалення'
        context['submit'] = 'Видалити'
        return context


def patient_add(request):
    context = {}
    context['who'] = 'паціента'
    context['active'] = 'patient-add'
    context['model_title'] = 'Пацієнти'
    context['title'] = 'Додавання'
    return render(request, 'tysk/add.html', context)


def doctor_add(request):
    context = {}
    context['who'] = 'лікаря'
    context['active'] = 'doctor-add'
    context['model_title'] = 'Лікарі'
    context['title'] = 'Додавання'
    context['submit'] = 'Додати'
    return render(request, 'tysk/add.html', context)
