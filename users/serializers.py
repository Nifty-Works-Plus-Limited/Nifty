from rest_framework import serializers
from common.helper_functions import get_current_time

from payments.serializers import PaymentSerializer
from .models import User


class UserSerializer(serializers.ModelSerializer):

    class Meta:
        model = User
        fields = '__all__'
        extra_kwargs = {
            'password': {'write_only': True}
        }
