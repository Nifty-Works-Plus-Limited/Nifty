from django.contrib.auth.models import AbstractUser
from django.db import models
from django.db.models.signals import post_init
from django.dispatch import receiver
from django.forms import ValidationError
from django.contrib.auth.hashers import make_password, check_password
import uuid
from payments.models import Payment
from oauth2_provider.models import AccessToken
# unique id to be used as pk for TeamMember table.


class User(AbstractUser):
    class Meta:
        db_table = 'auth_user'
    phone_number = models.CharField(max_length=32, blank=True, null=True)
    user_id = models.CharField(
        max_length=100, unique=True, default=None, editable=False)
    email = models.EmailField(unique=True)
    username = models.CharField(unique=True, default=None, max_length=100)
    phone_number = models.CharField(max_length=50, unique=True, null=True)
    is_email_verified = models.BooleanField(default=False)
    provider = models.CharField(max_length=100, default="Nifty")
    currency = models.CharField(max_length=5, default="KES")
    updated = models.DateTimeField(auto_now=True)
    date_joined = models.DateTimeField(auto_now_add=True)
    USERNAME_FIELD = 'email'
    # changes email to unique and blank to false

    REQUIRED_FIELDS = []  # removes email from REQUIRED_FIELDS

    def __str__(self):
        return self.email

    def save(self, *args, **kwargs):

        if self.username is None or self.username == '':
            self.username = self.email

        if self.user_id is None:
            self.user_id = uuid.uuid4().hex

        if self.password is not None:
            self.password = make_password(self.password)
        else:
            raise ValidationError('password cannot be empty')
        super().save(*args, **kwargs)


# SIGNALS
@receiver(signal=post_init, sender=User)
def update_access_token_scope(instance, **kwargs):
    latest_access_token = AccessToken.objects.filter(
        user_id=instance.id).order_by('-created').first()
    if latest_access_token is not None:
        scopes = latest_access_token.scope
        scopes_list = scopes.split()
        user_has_admin_scope = "admin" in scopes_list

        if (instance.is_staff and not user_has_admin_scope):
            latest_access_token.scope = scopes + " admin"
            latest_access_token.save(update_fields=['scope'])

        if (instance.is_staff == False and user_has_admin_scope):
            scopes_list.remove("admin")
            scope_without_admin = " ".join(scopes_list)
            latest_access_token.scope = scope_without_admin
            latest_access_token.save(update_fields=['scope'])
