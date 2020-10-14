import smtplib
import uuid
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit
from django import forms
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from app.models import Account
from testtask.settings import EMAIL_HOST, EMAIL_PORT, EMAIL_HOST_USER, EMAIL_HOST_PASSWORD


class AccountActivationForm(forms.Form):
    activation_code = forms.CharField(label="Введите код с письма", required=False, max_length=255)

    def __init__(self, *args, **kwargs):
        super(forms.Form, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.add_input(Submit('submit', 'Подтвердить', css_class='btn-primary'))
        self.helper.form_method = 'POST'


class AuthForm(AuthenticationForm):
    def __init__(self, *args, **kwargs):
        super(AuthForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.add_input(Submit('submit', 'Подтвердить', css_class='btn-primary'))
        self.helper.form_method = 'POST'


class RegistrationForm(UserCreationForm):
    referral_code = forms.CharField(label="Реферальный код", required=False, max_length=255)

    def __init__(self, *args, **kwargs):
        super(RegistrationForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.add_input(Submit('submit', 'Подтвердить', css_class='btn-primary'))
        self.helper.form_method = 'POST'

    class Meta:
        model = User
        fields = ("username", "email")

    def clean_referral_code(self):
        if Account.objects.count() > 5:
            if not self.cleaned_data.get('referral_code'):
                raise ValidationError('Обязательное поле')
            if not Account.get_referrer_by_code(self.cleaned_data.get('referral_code')):
                raise ValidationError('Неверный код')
        return self.cleaned_data.get('referral_code')

    def save(self, commit=True):
        user = super(RegistrationForm, self).save()
        referrer = Account.get_referrer_by_code(self.cleaned_data.get('referral_code'))
        activation_code = str(uuid.uuid4())
        acc = Account.objects.create(user_fk=user, referrer_fk=referrer, referral_code=str(uuid.uuid4()), activation_code=activation_code)
        smtpserver = smtplib.SMTP(EMAIL_HOST, EMAIL_PORT)
        smtpserver.ehlo()
        smtpserver.starttls()
        try:
            smtpserver.login(EMAIL_HOST_USER, EMAIL_HOST_PASSWORD)
            smtpserver.sendmail('Test', user.email, activation_code)
        except Exception:
            pass
        smtpserver.quit()
        if acc.referrer_fk:
            points = acc.referrer_fk.referrals.count() + 1
            u = acc
            data_to_update = []
            while (u is not None or u.referrer_fk is not None) and points > 0:
                rr = u.referrer_fk.referrer_fk
                if not rr:
                    u.referrer_fk.points += points
                    data_to_update.append(u.referrer_fk)
                    break
                else:
                    u.referrer_fk.points += 1
                    data_to_update.append(u.referrer_fk)
                    points -= 1
                    u = u.referrer_fk
            Account.objects.bulk_update(data_to_update, ['points'])
        return user
