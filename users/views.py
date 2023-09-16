import uuid
from django.http import HttpResponseBadRequest
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status, permissions, generics
from rest_framework.exceptions import AuthenticationFailed, ParseError, PermissionDenied, NotFound
from rest_framework.permissions import IsAuthenticated, AllowAny, IsAdminUser
from auth_server.utils import create_oauth2_acess_token_object_from_request, get_user_from_request
from common.constants import DEFAULT_PROVIDER, INVALID_PROVIDER, JWT_COOKIE_KEY, NO_EMAIL, NO_PASSWORD, NO_PROVIDER, VALID_PROVIDERS
from .models import User
from .serializers import UserSerializer
from oauth2_provider.contrib.rest_framework import TokenHasReadWriteScope, TokenHasScope
from django.contrib.auth.hashers import check_password


def is_valid_request_param(request):
    allowed_query_params = ['user_id', 'email', 'password']

    query_param = list(request.query_params.keys())

    # check if query param list is not empty and is valid
    if bool(query_param) and query_param[0] not in allowed_query_params:
        return False
    return True


def check_valid_payload_in_request(request):
    if "email" not in request.data.keys():
        raise ParseError(NO_EMAIL)
    if "password" not in request.data.keys():
        raise ParseError(NO_PASSWORD)

    if "provider" not in request.data.keys():
        raise ParseError(NO_PROVIDER)

    if type(request.data["password"]) is int:
        raise ParseError("Password must be a string")

    if request.data['provider'] not in VALID_PROVIDERS:
        raise ParseError(INVALID_PROVIDER)

    return


class UserList(APIView):
    permission_classes = [IsAdminUser, TokenHasScope]
    users = User.objects.all()
    serializer_class = UserSerializer
    required_scopes = ['admin']

    def get(self, request):
        if is_valid_request_param(request):
            serializer = UserSerializer(self.users, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        raise ParseError

    def post(self, request):
        serializer = UserSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(data=serializer.data, status=status.HTTP_201_CREATED)


class SignUpView(APIView):
    permission_classes = [AllowAny]
    users = User.objects.all()
    serializer_class = UserSerializer

    def post(self, request):
        check_valid_payload_in_request(request)

        email = request.data['email']
        password = request.data['password']
        user = self.users.filter(email=email).first()

        # if password is not given generate one
        if password is None:
            request.data['password'] = uuid.uuid4().hex
        # if user does not exist create user and get token
        if user is None:
            serializer = UserSerializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            token_object = create_oauth2_acess_token_object_from_request(
                request)

            response = {
                "user": serializer.data,
                "auth": token_object
            }

            return Response(data=response, status=status.HTTP_201_CREATED)

        serializer = UserSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        return Response(status=status.HTTP_200_OK)


class SignInView(APIView):
    permission_classes = [AllowAny]
    serializer_class = UserSerializer

    def post(self, request):
        check_valid_payload_in_request(request)
        email = request.data['email']
        password = request.data['password']
        provider = request.data["provider"]
        user = User.objects.filter(email=email).first()

        if user is None:
            if provider != DEFAULT_PROVIDER:
                # generate unique password
                request.data["password"] = uuid.uuid4().hex
                # save user in db
                serializer = UserSerializer(data=request.data)
                serializer.is_valid(raise_exception=True)
                serializer.save()
                # generate token for user
                token_object = create_oauth2_acess_token_object_from_request(
                    request)

                return Response(data=token_object, status=status.HTTP_201_CREATED)
            else:
                raise AuthenticationFailed("User not found!")
        if provider != DEFAULT_PROVIDER:
            # generate unique password
            request.data["password"] = uuid.uuid4().hex
            # update user password in db
            serializer = UserSerializer(data=request.data)
            serializer.update(instance=user, validated_data=request.data)
            # generate token for user
            token_object = create_oauth2_acess_token_object_from_request(
                request)
            return Response(data=token_object, status=status.HTTP_200_OK)

        if not check_password(password, user.password):
            raise AuthenticationFailed("Incorrect password!")
        else:
            token_object = create_oauth2_acess_token_object_from_request(
                request)

        return Response(data=token_object, status=status.HTTP_200_OK)


class SignOutView(APIView):
    def post(self, request):
        return Response()


class UpdatePassword(APIView):
    permission_classes = [AllowAny]
    serializer_class = UserSerializer

    def post(self, request):
        check_valid_payload_in_request(request)
        email = request.data['email']
        user = User.objects.filter(email=email).first()
        serializer = UserSerializer(data=request.data)
        # serializer.is_valid(raise_exception=True)
        serializer.update(instance=user, validated_data=request.data)
        return Response(data="password updated", status=status.HTTP_200_OK)


class UserInfo(APIView):
    permission_classes = [IsAuthenticated, TokenHasReadWriteScope]
    users = User.objects.all()
    serializer_class = UserSerializer

    def get(self, request):
        user = get_user_from_request(request)
        db_user = self.users.filter(id=user.id).first()
        if user == 0:
            raise NotFound("User not found")
        else:
            serializer = UserSerializer(db_user)
            return Response(data=serializer.data, status=status.HTTP_200_OK)
