from django.db import models
from django.contrib.auth.models import User 
from post.utils.core import upload_image_path, generate_slug
from django.dispatch import receiver
from django.db.models.signals import post_save
from rest_framework.authtoken.models import Token
from django.conf import settings
from django.utils.translation import gettext_lazy as _ 
from .tokens import get_token_generator
from django.contrib.auth import get_user_model
# Create your models here.


TOKEN_GENERATOR_CLASS = get_token_generator()

class Profile(models.Model):

    user = models.OneToOneField(User, on_delete=models.CASCADE)
    first_name = models.CharField(max_length=256)
    last_name = models.CharField(max_length=256)
    bio = models.CharField(max_length=256, blank=True, null=True)
    profile_pic = models.ImageField(upload_to=upload_image_path,blank=True,null=True)

    def __str__(self):
        return self.user.username

@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def create_auth_token(sender, instance=None, created=False, **kwargs):
    print('token',Token)
    if created:
        Token.objects.create(user=instance) 

__all__ = [
    'ResetPasswordToken',
    'get_password_reset_token_expiry_time',
    'get_password_reset_lookup_field',
    'clear_expired',
]

class ResetPasswordToken(models.Model):

    class Meta:
        verbose_name = _("Password Reset Token")
        verbose_name_plural = _("Password Reset Tokens")

    @staticmethod
    def generate_key():
        """ generates a pseudo random code using os.urandom and binascii.hexlify """
        return TOKEN_GENERATOR_CLASS.generate_token()

    id = models.AutoField(
        primary_key=True
    )

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        related_name='password_reset_tokens',
        on_delete=models.CASCADE,
        verbose_name=_("The User which is associated to this password reset token")
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name=_("When was this token generated")
    )

    # Key field, though it is not the primary key of the model
    key = models.CharField(
        _("Key"),
        max_length=64,
        db_index=True,
        unique=True
    )

    ip_address = models.GenericIPAddressField(
        _("The IP address of this session"),
        default="",
        blank=True,
        null=True,
    )
    user_agent = models.CharField(
        max_length=256,
        verbose_name=_("HTTP User Agent"),
        default="",
        blank=True,
    )

    def save(self, *args, **kwargs):
        if not self.key:
            self.key = self.generate_key()
        return super(ResetPasswordToken, self).save(*args, **kwargs)

    def __str__(self):
        return "Password reset token for user {user}".format(user=self.user)

def get_password_reset_token_expiry_time():
    """
    Returns the password reset token expirty time in hours (default: 24)
    Set Django SETTINGS.DJANGO_REST_MULTITOKENAUTH_RESET_TOKEN_EXPIRY_TIME to overwrite this time
    :return: expiry time
    """
    # get token validation time
    return getattr(settings, 'DJANGO_REST_MULTITOKENAUTH_RESET_TOKEN_EXPIRY_TIME', 24)


def get_password_reset_lookup_field():
    """
    Returns the password reset lookup field (default: email)
    Set Django SETTINGS.DJANGO_REST_LOOKUP_FIELD to overwrite this time
    :return: lookup field
    """
    return getattr(settings, 'DJANGO_REST_LOOKUP_FIELD', 'username')


def clear_expired(expiry_time):
    """
    Remove all expired tokens
    :param expiry_time: Token expiration time
    """
    ResetPasswordToken.objects.filter(created_at__lte=expiry_time).delete()

def eligible_for_reset(self):
    if not self.is_active:
        # if the user is active we dont bother checking
        return False

    if getattr(settings, 'DJANGO_REST_MULTITOKENAUTH_REQUIRE_USABLE_PASSWORD', True):
        # if we require a usable password then return the result of has_usable_password()
        return self.has_usable_password()
    else:
        # otherwise return True because we dont care about the result of has_usable_password()
        return True

# add eligible_for_reset to the user class
UserModel = get_user_model()
UserModel.add_to_class("eligible_for_reset", eligible_for_reset)




#########################################################
# SMS VERIFICATION
#########################################################

# Standard Library
import uuid

from django.utils.translation import ugettext_lazy as _



class UUIDModel(models.Model):
    """ An abstract base class model that makes primary key `id` as UUID
    instead of default auto incremented number.
    """

    id = models.UUIDField(primary_key=True, editable=False, default=uuid.uuid4)

    class Meta:
        abstract = True


class TimeStampedUUIDModel(UUIDModel):
    """An abstract base class model that provides self-updating
    ``created`` and ``modified`` fields with UUID as primary_key field.
    """

    created_at = models.DateTimeField(auto_now_add=True, editable=False)
    modified_at = models.DateTimeField(auto_now=True, editable=False)

    class Meta:
        abstract = True


class SMSVerification(TimeStampedUUIDModel):
    security_code = models.CharField(_("Security Code"), max_length=120)
    phone_number = models.CharField(_("Phone Number"), max_length = 64)
    session_token = models.CharField(_("Device Session Token"), max_length=500)
    is_verified = models.BooleanField(_("Security Code Verified"), default=False)

    class Meta:
        # db_table = "sms_verification"
        verbose_name = _("SMS Verification")
        verbose_name_plural = _("SMS Verifications")
        ordering = ("-modified_at",)
        unique_together = ("security_code", "phone_number", "session_token")

    def __str__(self):
        return "{}: {}".format(str(self.phone_number), self.security_code)

