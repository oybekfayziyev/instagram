from rest_framework import serializers
from .models import Follower, Following
from django.contrib.auth.models import User
      
class FollowerSerializer(serializers.ModelSerializer):
     
    class Meta:
        model = Follower
        fields = '__all__'

class FollowingSerializer(serializers.ModelSerializer):
    class Meta:
        model = Following
        fields = '__all__'