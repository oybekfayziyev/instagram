from django.db import models
from django.contrib.auth.models import User 
from post.models import Post 
# Create your models here.

class Comment(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    comment = models.CharField(max_length=512)
    created_date = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.user.username

