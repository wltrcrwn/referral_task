from django.contrib.auth import logout
from django.contrib.auth.views import LogoutView
from django.urls import path, include, re_path

from app.views import Login, Registration, home, generate_referral_code, AccountActivation

urlpatterns = [
    path('login/', Login.as_view(), name="login"),
    path('logout/', LogoutView.as_view(), name="logout"),
    path('registration/', Registration.as_view(), name="registration"),
    path('generate_referral_code/', generate_referral_code, name="generate_referral_code"),
    path('activate_account/', AccountActivation.as_view(), name="account_activation"),
    path('', home, name="home"),
]
