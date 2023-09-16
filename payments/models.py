from django.db import models
from django.db.models.signals import post_init
from django.dispatch import receiver
from common.helper_functions import get_current_time


class PaymentPlan(models.Model):
    plan = models.CharField(max_length=50)
    description = models.TextField()
    price = models.PositiveSmallIntegerField()
    duration = models.CharField(max_length=50, null=True, default=None)

    def __str__(self):
        return self.plan


class Payment(models.Model):
    transaction_reference = models.CharField(
        max_length=100, unique=True, primary_key=True)
    transaction_id = models.CharField(
        max_length=100, unique=True, default=None, null=True)
    currency = models.CharField(max_length=5, default="KES")
    redirect_url = models.TextField(default="")
    payment_options = models.CharField(max_length=100, default="card, mpesa")
    payment_link = models.TextField(default=None, null=True)
    payment_link_status = models.CharField(
        max_length=50, default=None, null=True)
    payment_link_message = models.CharField(
        max_length=50, default=None, null=True)
    payment_status = models.CharField(max_length=50, default=None, null=True)
    # payment active status
    active_status = models.BooleanField(default=False)
    # subscription active status
    sub_active_status = models.BooleanField(default=False)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    expires = models.DateTimeField(default=None, null=True)
    user = models.ForeignKey(
        "users.User", on_delete=models.CASCADE, null=True, related_name="user")
    plan = models.ForeignKey(
        PaymentPlan, on_delete=models.DO_NOTHING, null=True)

    def __str__(self):
        return self.transaction_reference


# SIGNALS
@receiver(signal=post_init, sender=Payment)
def update_payment_active_status(instance, **kwargs):
    if instance.expires is not None:
        payment_duration = instance.expires - get_current_time()
        is_active = payment_duration.total_seconds(
        ) > 0 and instance.payment_status == "successful"

        print(instance.user)
        instance.active_status = is_active
        instance.save(update_fields=['active_status'])
