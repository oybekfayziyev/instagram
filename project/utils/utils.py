import re
import importlib

def import_attribute(path):
    assert isinstance(path, str)
    pkg, attr = path.rsplit('.', 1)
    ret = getattr(importlib.import_module(pkg), attr)
    return ret


def is_email(email):
    regex = '^[a-z0-9]+[\._]?[a-z0-9]+[@]\w+[.]\w{2,3}$'
    print('email',email)
    if re.search(regex, email):
        return True
    else:
        return False

def is_phone_number(phone):
    regex = '(\d{3}[-\.\s]??\d{3}[-\.\s]??\d{4}|\(\d{3}\)\s*\d{3}[-\.\s]??\d{4}|\d{3}[-\.\s]??\d{4})'

    if re.search(regex, phone):
        return True;
    else:
        return False
