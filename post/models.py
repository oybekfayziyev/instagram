from django.db import models
from django.contrib.auth.models import User 

from location.models import Location
from .utils.core import upload_image_path, generate_slug

# Create your models here.

class PostExtraImage(models.Model):
	title = models.CharField(max_length = 64, null=True,blank=True)
	image = models.ImageField(upload_to = upload_image_path)
	post = models.ForeignKey('Post', null=True,blank=True, on_delete=models.CASCADE, related_name='images')

	class Meta:
		verbose_name_plural = 'Images'
        
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

