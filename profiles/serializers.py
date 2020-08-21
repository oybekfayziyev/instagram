from rest_framework import serializers
from django.contrib.auth.models import User
from datetime import timedelta

from django.core.exceptions import ValidationError
from django.http import Http404
from django.shortcuts import get_object_or_404 as _get_object_or_404
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
 

from .models import get_password_reset_token_expiry_time
from . import models


class RegisterSerializer(serializers.ModelSerializer):

    first_name = serializers.CharField(max_length = 64)
    class Meta:
        model = User
        fields = ['username','password', 'first_name']        
    
        extra_kwargs = {'password': {'write_only': True}}



__all__ = [
    'EmailSerializer',
    'PasswordTokenSerializer',
    'ResetTokenSerializer',
]


class UsernameSerializer(serializers.Serializer):
    username = serializers.CharField(max_length=128)


class PasswordValidateMixin:
    def validate(self, data):
        token = data.get('token')

        # get token validation time
        password_reset_token_validation_time = get_password_reset_token_expiry_time()

        # find token
        try:
            reset_password_token = _get_object_or_404(models.ResetPasswordToken, key=token)
        except (TypeError, ValueError, ValidationError, Http404,
                models.ResetPasswordToken.DoesNotExist):
            raise Http404(_("The OTP password entered is not valid. Please check and try again."))

        # check expiry date
        expiry_date = reset_password_token.created_at + timedelta(
            hours=password_reset_token_validation_time)

        if timezone.now() > expiry_date:
            # delete expired token
            reset_password_token.delete()
            raise Http404(_("The token has expired"))
        return data


class PasswordTokenSerializer(serializers.Serializer):
    password = serializers.CharField(label=_("Password"), style={'input_type': 'password'})
    # token = serializers.CharField()


class ResetTokenSerializer(PasswordValidateMixin, serializers.Serializer):
    token = serializers.CharField()


class PhoneSerializer(serializers.Serializer):
    phone_number = serializers.CharField(max_length=13)



class SMSVerificationSerializer(serializers.Serializer):
    phone_number = serializers.CharField(required=True)
    session_token = serializers.CharField(required=True)
    security_code = serializers.CharField(required=True)

    def validate(self, attrs):
        attrs = super().validate(attrs)
        phone_number = attrs.get("phone_number", None)
        security_code, session_token = (
            attrs.get("security_code", None),
            attrs.get("session_token", None),
        )
        backend = get_sms_backend(phone_number=phone_number)
        verification, token_validatation = backend.validate_security_code(
            security_code=security_code,
            phone_number=phone_number,
            session_token=session_token,
        )

        if verification is None:
            raise serializers.ValidationError(_("Security code is not valid"))
        elif token_validatation == backend.SESSION_TOKEN_INVALID:
            raise serializers.ValidationError(_("Session Token mis-match"))
        elif token_validatation == backend.SECURITY_CODE_EXPIRED:
            raise serializers.ValidationError(_("Security code has expired"))
        elif token_validatation == backend.SECURITY_CODE_VERIFIED:
            raise serializers.ValidationError(_("Security code is already verified"))

        return attrs
