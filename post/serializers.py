from rest_framework import serializers
from .models import Post
from location.serializers import LocationSerializer
from .utils.core import get_absolute_uri

class PostSerializer(serializers.ModelSerializer):
        
    class Meta:
        model = Post
        fields = ['id','user','image','description','location','like','slug']

class PostRetrieveSerializer(serializers.ModelSerializer):

    image = serializers.SerializerMethodField()    
    def get_image(self,post):             
        return get_absolute_uri(self,post)        
    
    location = LocationSerializer()    
    class Meta:
        model = Post
        fields = ['id','user', 'image', 'description', 'location', 'like','slug']
    
    