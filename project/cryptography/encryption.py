from .base import *
from django.conf import settings
import json
CRYPT_KEY = settings.CRYPT_KEY

class Encrypt:
    
    def key(self):
        return Fernet(CRYPT_KEY)
    
    def generate_key(self):
        return Fernet.generate_key()
    
    def encrypt(self,data):
        fernet_key = self.key()
        return fernet_key.encrypt(data.encode())
    
def json_dumps(data):
    return json.dumps(data)

def json_loads(data):
    return json.loads(data)