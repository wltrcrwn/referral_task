from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.forms import AuthenticationForm
from django.core.exceptions import ValidationError
from django.forms.utils import ErrorList
from django.shortcuts import render, redirect
# Create your views here.
from django.urls import reverse
from django.views import View
from app.forms import RegistrationForm, AuthForm, AccountActivationForm
from app.models import Account


def home(request):
    if request.user.is_authenticated:
        if request.user.account.active:
            top_table = Account.objects.all().order_by('-points')[:10]
            referrals = request.user.account.referrals
            return render(request, 'home.html', context={'top_table': top_table, 'referrals': referrals})
        else:
            return redirect('account_activation')
    else:
        return redirect('login')


class Login(View):
    def get(self, request):
        f = AuthForm()
        return render(request, 'login.html', context={'form': f})

    def post(self, request):
        f = AuthForm(request, **{'data': request.POST})
        if f.is_valid():
            _username = f.cleaned_data.get('username')
            _password = f.cleaned_data.get('password')
            user = authenticate(username=_username, password=_password)
            login(request, user)
            return redirect('home')
        else:
            return render(request, 'login.html', context={'form': f})


class Registration(View):
    def get(self, request):
        f = RegistrationForm()
        return render(request, 'registration.html', context={'form': f})

    def post(self, request):
        f = RegistrationForm(request.POST)
        if f.is_valid():
            user = f.save()
            login(request, user)
            return redirect('home')
        else:
            return render(request, 'registration.html', context={'form': f})


class AccountActivation(View):
    def get(self, request):
        if request.user.is_authenticated and not request.user.account.active:
            f = AccountActivationForm()
            return render(request, 'account_activation.html', context={'form': f})
        else:
            return redirect('home')

    def post(self, request):
        f = AccountActivationForm(request.POST)
        if f.is_valid():
            if request.user.account.activate_account(f.cleaned_data.get('activation_code')):
                return redirect('home')
        f.add_error('activation_code', ValidationError('Неверный код'))
        return render(request, 'account_activation.html', context={'form': f})


def generate_referral_code(request):
    if request.method == 'POST':
        code = request.user.account.generate_referral_code()
        return redirect('home')


def activate_account(request):
    code = request.POST.get('activation_code')
    if request.account.activate_account(code):
        return
