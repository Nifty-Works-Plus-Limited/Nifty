from django.contrib import admin

from payments.models import Payment, PaymentPlan

# Register your models here.
admin.site.register(Payment)
admin.site.register(PaymentPlan)
