from datetime import timedelta
import json
from rest_framework.permissions import IsAuthenticated, AllowAny, IsAdminUser
from oauth2_provider.contrib.rest_framework import TokenHasReadWriteScope, TokenHasScope
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from common.constants import JWT_COOKIE_KEY
from common.helper_functions import get_current_time
from payments.models import Payment, PaymentPlan
from payments.serializers import PaymentSerializer
from rest_framework.exceptions import AuthenticationFailed, NotFound, ParseError, ValidationError
from rest_framework.authentication import get_authorization_header
from auth_server.utils import get_user_from_request
import os
import requests
from payments.utils import generate_payment_info, save_payment_info, update_payment_info

from dotenv import load_dotenv

from users.models import User
from users.serializers import UserSerializer

load_dotenv()
base_url = os.environ.get("BASE_URL")
payment_token = os.environ.get("PAYMENT_TOKEN")


def is_valid_request_param(request):
    allowed_query_params = ['latest', 'user_id', 'users']

    query_param = list(request.query_params.keys())

    # check if query param list is not empty and is valid
    if bool(query_param) and query_param[0] not in allowed_query_params:
        return False
    return True


class PaymentList(APIView):
    permission_classes = [IsAdminUser, TokenHasScope]
    required_scopes = ['admin']
    payments = Payment.objects.select_related(
        "user").all().order_by("-created")
    users = User.objects.all().order_by("-date_joined")

    def get(self, request):
        if is_valid_request_param(request=request):
            if ("users" in request.query_params.keys()):
                if (request.query_params['users'] == "status"):
                    active_users = []
                    inactive_users = []
                    for user in self.users:
                        if self.payments.filter(
                                user_id=user.id).first() is not None:
                            active_user = {
                                "user": UserSerializer(user).data,
                                "payment_info": PaymentSerializer(self.payments.filter(
                                    user_id=user.id).first()).data
                            }
                            active_users.append(active_user)
                        else:
                            inactive_user = {
                                "user": UserSerializer(user).data,
                                "payment_info": PaymentSerializer(self.payments.filter(
                                    user_id=user.id).first()).data
                            }
                            inactive_users.append(inactive_user)
                    response = {
                        "active": active_users,
                        "inactive": inactive_users
                    }
                    return Response(response, status=status.HTTP_200_OK)

        serializer = PaymentSerializer(self.payments, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class PaymentInfo(APIView):
    def get(self, request):
        user = get_user_from_request(request)
        if is_valid_request_param(request=request):
            # if latest keyword is in params
            if ("user_id" in request.query_params.keys()):
                if request.query_params["user_id"] == "":
                    raise NotFound("user does not exist")
                else:
                    user_id = request.query_params["user_id"]
                    payment = Payment.objects.order_by(
                        '-created').filter(user_id=user_id)

                    if payment:
                        serializer = PaymentSerializer(payment, many=True)
                        return Response(data=serializer.data, status=status.HTTP_200_OK)
                    else:
                        raise NotFound(
                            "payment information for this user does not exist")
            if ("latest" in request.query_params.keys()):
                # if latest params is true
                if (request.query_params['latest'] == "true"):
                    payment = Payment.objects.filter(
                        user_id=user.id).order_by('-created').first()
                    serializer = PaymentSerializer(payment)
                    return Response(data=serializer.data, status=status.HTTP_200_OK)

            payment = Payment.objects.filter(user_id=user.id)
            serializer = PaymentSerializer(payment, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        raise ParseError


class PaymentPlanView(APIView):
    pass


class MakePayment(APIView):
    permission_classes = [TokenHasReadWriteScope]
    payment = Payment
    serializer_class = PaymentSerializer

    def post(self, request):
        user = get_user_from_request(request)
        plan_id = request.data['plan_id']
        redirect_url = request.data['redirect_url']

        if user:
            active_payments = Payment.objects.filter(
                user_id=user.id, active_status=True).first()
            print(active_payments)
            if active_payments is None:
                payment_info = generate_payment_info(
                    user=user,
                    plan_id=plan_id,
                    redirect_url=redirect_url
                )

                save_payment_info(plan_id, payment_info, user)

                result = requests.post(
                    url=base_url+"/payments",
                    json=payment_info,
                    headers={"Authorization": "Bearer " + payment_token}
                )

                post_result = json.loads(result.content)

                serializer = update_payment_info(payment_info, post_result)

                response = {
                    "status": serializer.data.get("payment_link_status"),
                    "link": serializer.data.get("payment_link")
                }

                return Response(response, status=status.HTTP_200_OK)
            else:
                return Response(data="An active payment already exists", status=status.HTTP_409_CONFLICT)
        return AuthenticationFailed("Unauthorized user")


class CancelSubscription(APIView):
    permission_classes = [TokenHasReadWriteScope]
    payment = Payment
    serializer_class = PaymentSerializer

    def get(self, request):
        user = get_user_from_request(request)
        payment_instance = Payment.objects.filter(
            user_id=user.id, active_status=True, sub_active_status=True).first()
        if payment_instance is None:
            raise NotFound("Subscription does not exist for this user")
        else:
            # update  payment
            sub_info = {
                "transaction_reference": payment_instance.transaction_reference,
                "sub_active_status": False,
            }
            serializer = PaymentSerializer(
                instance=payment_instance,
                data=sub_info
            )
            print(payment_instance)
            serializer.is_valid(raise_exception=True)
            serializer.save()

            return Response(data="Subscription is cancelled", status=status.HTTP_200_OK)


class VerifyPayment(APIView):
    permission_classes = [TokenHasReadWriteScope]
    payment = Payment
    serializer_class = PaymentSerializer

    def is_valid_request_param(self, request):
        allowed_query_params = ['tx_ref']

        # if no query parameter is passed
        if len(request.query_params.keys()) == 0:
            return False
        query_param = list(request.query_params.keys())

        # check if query param list is not empty and is valid
        if bool(query_param) and query_param[0] not in allowed_query_params:
            return False
        return True

    def get(self, request):
        user = get_user_from_request(request)

        if (self.is_valid_request_param(request)):
            transaction_ref = request.query_params["tx_ref"]

        else:
            raise ParseError

        payment_instance = Payment.objects.filter(
            transaction_reference=transaction_ref, user_id=user.id).first()
        if payment_instance is None:

            raise NotFound("Payment does not exist for this user")
        else:

            verification_url = "{base_url}/transactions/verify_by_reference?tx_ref={transaction_ref}"
            verify_payment_url = verification_url.format(
                base_url=base_url, transaction_ref=transaction_ref)

            result = requests.get(
                url=verify_payment_url,
                headers={"Authorization": "Bearer " + payment_token}
            )

            payment_result = json.loads(result.content)

            payment_plan = PaymentPlan.objects.filter(
                id=payment_instance.plan_id).first()

            payment_plan_duration = payment_plan.duration
            payment_expiry = payment_instance.created + \
                timedelta(seconds=int(payment_plan_duration))

            if (payment_result.get("data")):

                payment_duration = payment_expiry - get_current_time()
                payment_is_active = payment_duration.total_seconds() > 0 and payment_result.get(
                    "data").get("status") == "successful"

                transaction_info = {
                    "transaction_reference": transaction_ref,
                    "transaction_id": payment_result.get("data").get("id"),
                    "payment_status": payment_result.get("data").get("status"),
                    "active_status": payment_is_active,
                    "sub_active_status": payment_is_active,
                    "expires": payment_expiry
                }

                # update  transaction
                serializer = PaymentSerializer(
                    instance=payment_instance,
                    data=transaction_info
                )
                serializer.is_valid(raise_exception=True)
                serializer.save()

                return Response(data="Transaction is verified", status=status.HTTP_200_OK)

            else:
                transaction_info = {
                    "transaction_reference": transaction_ref,
                    "transaction_id": None,
                    "payment_status": "failed",
                    "expires": payment_expiry
                }
                # update  transaction
                serializer = PaymentSerializer(
                    instance=payment_instance,
                    data=transaction_info
                )
                serializer.is_valid(raise_exception=True)
                serializer.save()

                raise NotFound("No verified transaction found")
