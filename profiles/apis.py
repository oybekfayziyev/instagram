from rest_framework import viewsets
# from project.api.decorators import api_view_serializer_class_getter, api_view_serializer_class
# from project.api.settings import registration_settings
from django.core.exceptions import ObjectDoesNotExist
# from project.api.exceptions import LoginInvalid

from rest_framework.response import Response
# from django.contrib import auth
from rest_framework.views import APIView
# from rest_framework.settings import api_settings
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.authentication import TokenAuthentication, BaseAuthentication
from .serializers import RegisterSerializer
from django.contrib.auth.models import User
from django.contrib.auth import logout as django_logout

from project.cryptography.encryption import (Encrypt, 
                                        json_dumps,
                                        json_loads
                                    )
from project.cryptography.decryption import Decrypt

from project.utils.utils import is_email, is_phone_number

from . import signals
###
from datetime import timedelta
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.contrib.auth.password_validation import validate_password, get_password_validators
from django.utils.translation import gettext_lazy as _
from django.utils import timezone 
from django.conf import settings
from rest_framework import status, exceptions
from rest_framework.generics import GenericAPIView
from rest_framework.response import Response

from .serializers import UsernameSerializer, PasswordTokenSerializer, ResetTokenSerializer
from .models import ResetPasswordToken, clear_expired, get_password_reset_token_expiry_time, \
    get_password_reset_lookup_field

from django.core.mail import BadHeaderError, EmailMultiAlternatives
from .signals import reset_password_token_created, pre_password_reset, post_password_reset

EMAIL_HOST_USER = settings.EMAIL_HOST_USER
EMAIL_SUBJECT = settings.EMAIL_SUBJECT
EMAIL_MESSAGE = settings.EMAIL_MESSAGE

class LogoutApi(APIView):

    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self,request):
        try:
            request.user.auth_token.delete()
        except (AttributeError, ObjectDoesNotExist):
            Response(status=status.HTTP_400_BAD_REQUEST)
        django_logout(request)
        return Response({"success": "Successfully logged out."}, status=status.HTTP_200_OK)

class RegisterViewSet(viewsets.ModelViewSet):

    permission_classes = [AllowAny]
    serializer_class = RegisterSerializer  

    def get_object(self, username):
        try:
            user = User.objects.get(username = username)
        except ObjectDoesNotExist:
            user = None
        
        return user

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data = request.data)
        serializer.is_valid(raise_exception = True)        
        user = self.get_object(request.data['username'])
      
        if not user:
            user = self.perform_create(request.data['username'],
                                request.data['password'], 
                                request.data['first_name']
                            )
            string_json_data = json_dumps(serializer.data)                             
            data = Encrypt().encrypt(string_json_data)     

            original_data = json_loads(data = Decrypt().decrypt(data))
            print('sent data', original_data)
            return Response({'data':data}, status=status.HTTP_201_CREATED)
        
        return Response({'data':'Username is already exist'},status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    def perform_create(self, username, password, first_name):

        create_user = User.objects.create_user(
            username=username,
            password=password,
            first_name = first_name
        )
        return create_user



User = get_user_model()

__all__ = [
    'ResetPasswordValidateToken',
    'ResetPasswordConfirm',
    'ResetPasswordRequestToken',
    'reset_password_validate_token',
    'reset_password_confirm',
    'reset_password_request_token'
]

HTTP_USER_AGENT_HEADER = getattr(settings, 'DJANGO_REST_PASSWORDRESET_HTTP_USER_AGENT_HEADER', 'HTTP_USER_AGENT')
HTTP_IP_ADDRESS_HEADER = getattr(settings, 'DJANGO_REST_PASSWORDRESET_IP_ADDRESS_HEADER', 'REMOTE_ADDR')


class ResetPasswordValidateToken(GenericAPIView):
    """
    An Api View which provides a method to verify that a token is valid
    """
    throttle_classes = ()
    permission_classes = ()
    serializer_class = ResetTokenSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        return Response({'status': 'OK'})


class ResetPasswordConfirm(GenericAPIView):
    """
    An Api View which provides a method to reset a password based on a unique token
    """
    throttle_classes = ()
    permission_classes = ()
    serializer_class = PasswordTokenSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data)
        
        serializer.is_valid(raise_exception=True)
       
        password = serializer.validated_data['password']
        token = self.kwargs.get('token')

        # find token
        reset_password_token = ResetPasswordToken.objects.filter(key=token).first()
        if reset_password_token:
        # change users password (if we got to this code it means that the user is_active)
            if reset_password_token.user.eligible_for_reset():
                pre_password_reset.send(sender=self.__class__, user=reset_password_token.user)
                try:
                    # validate the password against existing validators
                    validate_password(
                        password,
                        user=reset_password_token.user,
                        password_validators=get_password_validators(settings.AUTH_PASSWORD_VALIDATORS)
                    )
                except ValidationError as e:
                    # raise a validation error for the serializer
                    raise exceptions.ValidationError({
                        'password': e.messages
                    })

                reset_password_token.user.set_password(password)
                reset_password_token.user.save()
                post_password_reset.send(sender=self.__class__, user=reset_password_token.user)

            # Delete all password reset tokens for this user
            ResetPasswordToken.objects.filter(user=reset_password_token.user).delete()

            return Response({'status': 'OK'})
        
        return Response({'status' : 'Token not found'},status=status.HTTP_404_NOT_FOUND)


class ResetPasswordRequestToken(GenericAPIView):

    """
    An Api View which provides a method to request a password reset token based on an e-mail address
    Sends a signal reset_password_token_created when a reset token was created
    """

    throttle_classes = ()
    permission_classes = ()
    serializer_class = UsernameSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data)
        print(request.data)
        serializer.is_valid(raise_exception=True)
        username = serializer.validated_data['username']

        # before we continue, delete all existing expired tokens
        password_reset_token_validation_time = get_password_reset_token_expiry_time()
        # datetime.now minus expiry hours
        now_minus_expiry_time = timezone.now() - timedelta(hours=password_reset_token_validation_time)

        # delete all tokens where created_at < now - 24 hours
        clear_expired(now_minus_expiry_time)

        print(get_password_reset_lookup_field())
        # find a user by username address (case insensitive search)
        users = User.objects.filter(**{'{}__iexact'.format(get_password_reset_lookup_field()): username})
         
        active_user_found = False

        # iterate over all users and check if there is any user that is active
        # also check whether the password can be changed (is useable), as there could be users that are not allowed
        # to change their password (e.g., LDAP user)
        for user in users:
            if user.eligible_for_reset():
                active_user_found = True
                 
        print(getattr(settings, 'DJANGO_REST_PASSWORDRESET_NO_INFORMATION_LEAKAGE', False))
        # No active user found, raise a validation error
        # but not if DJANGO_REST_PASSWORDRESET_NO_INFORMATION_LEAKAGE == True
        if not active_user_found and not getattr(settings, 'DJANGO_REST_PASSWORDRESET_NO_INFORMATION_LEAKAGE', False):
            raise exceptions.ValidationError({
                'username': [_(
                    "We couldn't find an account associated with that email. Please try a different e-mail address.")],
            })

        # last but not least: iterate over all users that are active and can change their password
        # and create a Reset Password Token and send a signal with the created token
        for user in users:
            if user.eligible_for_reset():
                # define the token as none for now
                token = None

                # check if the user already has a token
                if user.password_reset_tokens.all().count() > 0:
                    # yes, already has a token, re-use this token
                    token = user.password_reset_tokens.all()[0]
                else:
                    # no token exists, generate a new token
                    token = ResetPasswordToken.objects.create(
                        user=user,
                        user_agent=request.META.get(HTTP_USER_AGENT_HEADER, ''),
                        ip_address=request.META.get(HTTP_IP_ADDRESS_HEADER, ''),
                    )
                
                if is_email(username):
                    self.send_email(request.data['username'], token)

                    # send a signal that the password token was created
                    # let whoever receives this signal handle sending the email for the password reset
                    reset_password_token_created.send(sender=self.__class__, instance=self, reset_password_token=token)

                elif is_phone_number(user.username):
                    return Response({'data':'Phone number'},status=status.HTTP_200_OK)
        # done  

        return Response({'status': 'OK'})

    def send_email(self, username, token):
        subject = EMAIL_SUBJECT
        html_content = EMAIL_MESSAGE.format(
            link = 'localhost:8000',    
            link_token = token.key,         
            username = username
        )
        # html_content = '<a href="http://localhost:8000/api/profile/reset-password/confirm/%s/">localhost:8000/api/profile/reset-password/confirm/%s/</a>'% (token.key,token.key)
        from_email = EMAIL_HOST_USER
        if subject and html_content and from_email:
            try:
                msg = EmailMultiAlternatives(subject, html_content, from_email, [username])
                msg.attach_alternative(html_content, "text/html")
                msg.send()
                
            except BadHeaderError:
                return Response({'data':'Invalid header found.'},status=status.HTTP_400_BAD_REQUEST)
            return Response({'data':'Email sent'},status=status.HTTP_200_OK)
        else:
            # In reality we'd use a form class
            # to get proper validation errors.
            return Response({'data':'Make sure all fields are entered and valid.'},status=status.HTTP_400_BAD_REQUEST)
 
reset_password_validate_token = ResetPasswordValidateToken.as_view()
reset_password_confirm = ResetPasswordConfirm.as_view()
reset_password_request_token = ResetPasswordRequestToken.as_view()





##################################################################
# SEND THE CODE TO PHONE NUMBER API
##################################################################

from rest_framework.decorators import action
from .serializers import PhoneSerializer, SMSVerificationSerializer
from .services import send_security_code_and_generate_session_token


class VerificationViewSet(viewsets.ModelViewSet):

    serializer_class = PhoneSerializer
    permission_classes = [AllowAny]

    def create(self, request, *args, **kwargs):
        print('A')
        serializer = self.get_serializer(data=request.data)
        print('serializer',serializer)
        serializer.is_valid(raise_exception=True)
        print('send_security')
        session_token = send_security_code_and_generate_session_token(
            str(request.data['phone_number'])
        )
        print('sent')
        
        return Response({"session_token": session_token},status=status.HTTP_200_OK)

verification_viewset = VerificationViewSet.as_view({'post':'create'})

class VerificationByVerifyViewset(viewsets.ModelViewSet):
    serializer_class = SMSVerificationSerializer
    permisssion_classes = [AllowAny]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        return Response({"message": "Security code is valid."})

verification_by_verify = VerificationViewSet.as_view({'post':'create'})