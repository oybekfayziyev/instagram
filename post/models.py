from django.db import models
from django.contrib.auth.models import User 
from rest_framework.authtoken.models import Token
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.conf import settings
from location.models import Location
from .utils.core import upload_image_path, generate_slug

# Create your models here.

class Post(models.Model):

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    image = models.ImageField(upload_to=upload_image_path)
    description = models.CharField(max_length=512,blank=True,null=True)    
    location = models.ForeignKey(Location, on_delete=models.CASCADE, blank=True, null=True)
    like = models.ManyToManyField(User, related_name="like",blank=True)
    slug = models.SlugField(default=generate_slug, unique=True, blank=True,null=True)
    created_date = models.DateTimeField(auto_now_add=True, blank=True,null=True)
    update_date = models.DateField(auto_now=True)
    
    def __str__(self):
        return self.user.username

class Profile(models.Model):

    user = models.OneToOneField(User, on_delete=models.CASCADE)
    first_name = models.CharField(max_length=256)
    last_name = models.CharField(max_length=256)
    bio = models.CharField(max_length=256)
    profile_pic = models.ImageField(upload_to=upload_image_path,blank=True,null=True)

    def __str__(self):
        return self.user.username

@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def create_auth_token(sender, instance=None, created=False, **kwargs):
    print('token',Token)
    if created:
        Token.objects.create(user=instance)