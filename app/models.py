from django.contrib.auth.models import User
from django.db import models
import uuid


class Account(models.Model):
    user_fk = models.OneToOneField(User, on_delete=models.CASCADE)
    referral_code = models.CharField(max_length=255, null=True)
    points = models.PositiveIntegerField(default=0)
    referrer_fk = models.ForeignKey('self', on_delete=models.SET_NULL, null=True)
    activation_code = models.CharField(max_length=255, null=True)
    active = models.BooleanField(default=False)

    def generate_referral_code(self):
        code = uuid.uuid4()
        self.referral_code = code
        self.save()
        return code

    @staticmethod
    def get_referrer_by_code(code):
        try:
            return Account.objects.get(referral_code=code)
        except Exception as e:
            print(str(e))
            return None

    @property
    def referrals(self):
        return Account.objects.filter(referrer_fk_id=self.id)

    def activate_account(self, code):
        if code == self.activation_code:
            self.active = True
            self.save()
            return True
        else:
            return False
