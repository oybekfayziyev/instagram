from django.db import models
from django.contrib.auth.models import User 
from django.utils import timezone
# Create your models here.

class Follower(models.Model):
    
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    followers = models.ManyToManyField(User, related_name='followers')
    created_date = models.DateTimeField(auto_now_add=True, blank=True, null=True)
    updated_date = models.DateTimeField(auto_now=True, blank=True, null=True)

    def update(self,instance,follower):
    
        instance.updated_date = timezone.now()
        instance.followers.add(follower)     
        instance.save()
  
        return True

    def create(self,instance,user,follower):
       
        follower_obj = instance.objects.create(
            user = user,
            created_date = timezone.now()
        )        
        follower_obj.followers.add(follower)        
        return follower_obj

    def remove(self, instance,follower):
    
        instance.followers.remove(follower)        
        instance.save()

        if not instance.followers.all():
            instance.delete()
      
        return True

    def __str__(self):
        return self.user.username

class Following(models.Model):

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='user')
    following = models.ManyToManyField(User, related_name="following")
    created_date = models.DateTimeField(auto_now_add=True, blank=True,null=True)
    updated_date = models.DateTimeField(auto_now = True, blank=True,null=True)

    def __str__(self):
        return self.user.username


