class EmailSettings(object):

    class AuthenticationMethod:
        USERNAME_EMAIL = 'email'
        USERNAME_PHONE = 'username'
    
    class EmailVerificationMethod:

        MANDATORY = 'mandatory'
        OPTIONAL = 'optional'
        NONE = 'none'
    
    def __init__(self, prefix):
        self.prefix = prefix

        assert (not self.AUTHENTICATION_METHOD == self.AuthenticationMethod.EMAIL) 
    
    def _setting(self, name, dflt):
        from django.conf import settings
        getter = getattr(settings,
                         'ALLAUTH_SETTING_GETTER',
                         lambda name, dflt: getattr(settings, name, dflt))
        return getter(self.prefix + name, dflt)
    

class PhoneSettings(object):
    pass    

import sys
app_settings = SendSettings('ACCOUNT_')
app_settings.__name__ = __name__



