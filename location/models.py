from django.db import models
from django.contrib.auth.models import User 

# Create your models here.

class Location(models.Model):
    
    lattitude = models.CharField(max_length=32,null=True,blank=True)
    longitude = models.CharField(max_length=32, null=True,blank=True)

    def __str__(self):
        return f"{self.lattitude}:{self.longitude}".format(self.lattitude, self.longitude)


