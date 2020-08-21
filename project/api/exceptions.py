from rest_framework.exceptions import APIException
from django.utils.translation import gettext_lazy as _
from django.core.exceptions import ObjectDoesNotExist

class BadRequest(APIException):
    status_code = 400
    default_detail = _("Bad Request")
    default_code = 'bad-request'

class AuthTokenError(BadRequest):
    default_detail = _("Could not process authentication token")
    default_code = "auth-token-error"

class AuthTokenNotFound(AuthTokenError):
    default_detail = _("Authentication token not found")
    default_code = "auth-token-not-found"

class LoginInvalid(BadRequest):
    default_detail = _("Login Invalid error")
    default_code = "login-invalid"

class ModelExceptions:

    def object_does_not_exist(self, klass, fields = None, attributes = None):
        try:
            model = klass.objects.get()
        except ObjectDoesNotExist:
            model = None 
        
        return model 

    def get_fields(self, fields, attributes):
        _list = []
        for field, index in enumerate(fields):
            _list.append("%s = %s" % (field, attributes[index]))
        
        return _list
    
    def split_list_with_equal_op(self, _list):
        pass
            
            

