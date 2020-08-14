from .base import *
from .encryption import Encrypt

class Decrypt(Encrypt):
    
    def decrypt(self,data):
        fernet_key = self.key()
        return fernet_key.decrypt(data).decode()   
    

