import requests
from django.contrib.auth import get_user_model
from django.views.decorators.csrf import ensure_csrf_cookie 
from hashlib import md5
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.exceptions import ValidationError
from rest_framework.generics import get_object_or_404
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.viewsets import ModelViewSet

from .authentication import SafeJWTAuthentication
from .constants import *
from .models import User, Role, Verification
from .my_logger import logger
from .permissions import IsCreationOrIsAuthenticated
from .serializers import UserSerializer, UserResponseSerializer, VerificationSerializer
from my_exceptions import DataNotExist


@api_view(['POST'])
@permission_classes([AllowAny])
@ensure_csrf_cookie
def login_view(request):
    try:
        username = request.data.get('username')
        password = request.data.get('password')
        response = Response()
        if (username is None) or (password is None):
            raise exceptions.AuthenticationFailed(
                'username and password required')
    
        user = User.objects.filter(username=username).first()
        if user is None:
            raise exceptions.AuthenticationFailed('user not found')
        if not user.password == md5(password.encode()).hexdigest():
            raise exceptions.AuthenticationFailed('wrong password')
    
        serialized_user = UserSerializer(user).data
    
        access_token = generate_access_token(user)
        refresh_token = generate_refresh_token(user)
    
        response.set_cookie(key='refreshtoken', value=refresh_token, httponly=True)
        response.data = {
            'access_token': access_token,
            'user': serialized_user,
        }
    
        return response
    except Exception as e:
        raise DataNotExist(e.__str__())


class UserViewSets(ModelViewSet):
    """
    A UserViewSets that provides default `create()`, `retrieve()`, `update()`,
    `partial_update()`, `destroy()` and `list()` actions for that respect user object.
    If you want changes in that default methods we can override it is possible.
    """
    queryset = User.objects.filter(is_deleted=False)
    serializer_class = UserSerializer
    authentication_classes = (SafeJWTAuthentication,)
    permission_classes = (IsCreationOrIsAuthenticated,)

    def create(self, request, *args, **kwargs):
        """
        This method overrides the default create method in viewSet
        Added some fields like Created by this who crates this object
        :param request: post request for create user
        :return: if request was success returns response object of the user with status code
                 else return error message with status code
        """
        try:
            if Verification.objects.filter(email=request.data[EMAIL]):
                role = get_object_or_404(Role, name=request.data[ROLE][0])
                request.data[ROLE] = [role.id]
                serializer = UserSerializer(data=request.data)
                serializer.is_valid(raise_exception=True)
                instance = serializer.save()
                serializer = UserSerializer(instance, data=request.data)
                serializer.is_valid(raise_exception=True)
                serializer.save(created_by=instance, updated_by=instance)
                logger.info(CREATED_SUCCESS)
                return Response({DETAIL: serializer.data}, status=status.HTTP_201_CREATED)
            else:
                return Response({DETAIL: VERIFY_MAIL}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        except Exception as e:
            raise DataNotExist(e.__str__())
            
    def retrieve(self, request, *args, **kwargs):
        """
        This method overrides the default update method in viewSet,
        and we can get the user objects here
        :param request: get request for retrieve user
        :return: if request was success returns response object of the user with status code
                 else return error message with status code
        """
        try:
            instance = User.objects.filter(pk=kwargs.get(PK))
            if not instance:
                raise DataNotExist(USER_NOT_EXIST)
            serializer = UserResponseSerializer(instance, many=true)
            logger.info(RETRIEVED_SUCCESS)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Exception as e:
            raise DataNotExist(e.__str__())
        
    def list(self, request, *args, **kwargs):
        """
        This method overrides the default list method in viewSet
        Added some fields like Updated by this who crates this object
        :param request: put request for list the user
        :return: if request was success returns response object of the user with status code
                 else return error message with status code
        """
        try:
            queryset = self.filter_queryset(self.get_queryset())
            if queryset:
                page = self.paginate_queryset(queryset)
                if page is not None:
                    serializer = self.get_serializer(page, many=True)
                    logger.info()
                    return self.get_paginated_response(serializer.data)
    
                serializer = self.get_serializer(queryset, many=True)
                logger.info(RETRIEVED_SUCCESS)
                return Response(serializer.data)
            raise DataNotExist(USER_NOT_EXIST)
        except Exception as e:
            raise DataNotExist(e.__str__())

    def update(self, request, *args, **kwargs):
        """
        This method overrides the default update method in viewSet
        Added some fields like Updated by this who crates this object
        :param request: put request for update user
        :return: if request was success returns response object of the user with status code
                 else return error message with status code
        """
        try:
            updated_by = request.headers.get(USER_ID)
            instance = self.get_object()
            value = request.data[ROLE]
            request.data[ROLE] = []
            for i in value:
                role = Role.objects.get(name=i)
                request.data[ROLE].append(role.id)
            instance.updated_by = User.objects.get(is_deleted=False, id=updated_by)
            serializer = self.get_serializer(instance, data=request.data)
            serializer.is_valid(raise_exception=True)
            self.perform_update(serializer)
            logger.info(UPDATED_SUCCESS, status.HTTP_200_OK)
            return Response(serializer.data)
        except Exception as e:
            raise DataNotExist(e.__str__())


class DeleteUser(APIView):
    """
    Api view class for delete this object using api request from user
    """
    authentication_classes = (SafeJWTAuthentication,)
    permission_classes = (IsAuthenticated,)

    @staticmethod
    def delete(request, pk):
        """
        here we perform soft delete of the object the
        state of the object is changed to in active
        :param request: delete request
        :param pk: id for delete
        :return: success message response if id present in the table
                 else return error message with status code
        """
        try:
            user = User.objects.get(pk=pk)
            if not user.is_deleted:
                user.is_deleted = True
                User.save(user)
                logger.info(DELETED_SUCCESS)
                return Response({DETAIL: DELETED_SUCCESS})
            else:
                logger.error(USER_NOT_EXIST)
                return Response({DETAIL: USER_NOT_EXIST}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            raise DataNotExist(e.__str__())


def generate_otp(mail):
    """
    This is a helper function to send otp to session stored phones or
    passed phone number argument.
    """

    import hashlib
    try:
        mail = abs(hash(int(hashlib.sha1(mail.encode(UTF)).hexdigest(), 16) % (10 ** 8)))
        return int(mail + 2341 / 275 * int(str(mail)[5]) - 12345)
    except Exception as e:
        raise DataNotExist(e.__str__())


def send_mail(mail):
    import smtplib
    try:
        s = smtplib.SMTP(SMTP, 587)
        s.starttls()
        message = f"Here is your otp for verify your mail {generate_otp(mail)}"
        s.login(MAIL_ID, SECRET)
        s.sendmail(SYMBOL, mail, message)
    except Exception as e:
        raise DataNotExist(e.__str__())


class SendOTP(APIView):

    @staticmethod
    def post(request):
        try:
            email = request.data.get(EMAIL)
    
            if email:
                user = Verification.objects.filter(email__iexact=email)
    
                if not user:
                    send_mail(email)
                    logger.info(OTP_SENT)
                    return Response({
    
                        DETAIL: OTP_SENT,
                        STATUS: status.HTTP_200_OK,
                    })
                else:
                    logger.warn(MAIL_ALREADY_EXIST)
                    return Response({
                        DETAIL: MAIL_ALREADY_EXIST,
                        STATUS: status.HTTP_400_BAD_REQUEST,
                    }
                    )
            else:
                logger.warn(EMAIL_REQUIRED)
                return Response({
                    DETAIL: EMAIL_REQUIRED,
                    STATUS: status.HTTP_400_BAD_REQUEST,
                })
        except Exception as e:
            raise DataNotExist(e.__str__())


# verify otp
class VerifyOTP(APIView):
    @staticmethod
    def post(request):
        try:
            email = request.data[EMAIL]
            otp = request.data[OTP]
            if otp == generate_otp(email):
                instance = VerificationSerializer(data=request.data)
                instance.is_valid()
                instance.save()
                logger.info(OTP_VERIFICATION_SUCCESS)
                return Response({DETAIL: OTP_VERIFICATION_SUCCESS}, status=status.HTTP_200_OK)
            else:
                logger.warn(OTP_DOES_NOT_MATCH)
                return Response({DETAIL: OTP_DOES_NOT_MATCH}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            raise DataNotExist(e.__str__())
