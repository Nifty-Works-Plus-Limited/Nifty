from common.helper_functions import get_current_time
from payments.serializers import PaymentSerializer
from users.models import User
from common.constants import LOGO_URL, PAYMENT_OPTIONS, PAYMENT_TITLE
from payments.models import Payment, PaymentPlan
from parameters.models import Parameter
from dotenv import load_dotenv
import uuid
from rest_framework.response import Response
from datetime import datetime, timedelta


load_dotenv()


def generate_payment_info(user, plan_id, redirect_url):
    logo_url = Parameter.objects.filter(parameter=LOGO_URL).first().description
    payment_title = Parameter.objects.filter(
        parameter=PAYMENT_TITLE).first().description
    payment_options = Parameter.objects.filter(
        parameter=PAYMENT_OPTIONS).first().description
    uid = str(uuid.uuid4())
    firstname = user.first_name
    lastname = user.last_name

    if not firstname:
        firstname = 'user' + user.user_id
    if not lastname:
        lastname = ''

    # check if uuid exists
    while Payment.objects.filter(transaction_reference=uid).exists():
        # if exists generate another
        uid = uuid.uuid4()

    payment_plan = PaymentPlan.objects.filter(id=plan_id).first()

    payment_info = {
        "tx_ref": uid,
        "amount": payment_plan.price,
        "currency": user.currency,
        "redirect_url": redirect_url,
        "meta": {
            "consumer_id": user.user_id,
        },
        "customer": {
            "email": user.email,
            "phonenumber": user.phone_number,
            "name": firstname + " " + lastname
        },
        "customizations": {
            "title": payment_title,
            "logo": logo_url
        },
        "payment_options": payment_options

    }

    return payment_info


def save_payment_info(plan_id, payment_info, user):

    db_payment = {
        "transaction_reference": payment_info.get("tx_ref"),
        "currency": payment_info.get("currency"),
        "redirect_url": payment_info.get("redirect_url"),
        "payment_options": payment_info.get("payment_options"),
        "user": user.id,
        "plan": plan_id,
        "created": get_current_time()

    }
    serializer = PaymentSerializer(data=db_payment, many=False)
    serializer.is_valid(raise_exception=True)
    serializer.save()


def update_payment_info(payment_info, post_result):
    payment_instance = Payment.objects.filter(
        transaction_reference=payment_info.get("tx_ref")).first()

    db_payment_update = {
        "transaction_reference": payment_info.get("tx_ref"),
        "redirect_url": payment_info.get("redirect_url"),
        "payment_link": post_result.get("data").get("link"),
        "payment_link_status": post_result.get("status"),
        "payment_link_message": post_result.get("message"),
    }

    serializer_class = PaymentSerializer(
        instance=payment_instance, data=db_payment_update)

    serializer_class.is_valid(raise_exception=True)
    serializer_class.save()
    return serializer_class
