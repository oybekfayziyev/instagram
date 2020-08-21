from .serializers import FollowingSerializer, FollowerSerializer
from rest_framework import viewsets
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.authentication import TokenAuthentication
from django.core.exceptions import ObjectDoesNotExist
from .models import Follower, User, Following
from django.shortcuts import get_object_or_404
from django.utils import timezone
from rest_framework.response import Response
from project.cryptography.encryption import (Encrypt, 
                                        json_dumps,
                                        json_loads
                                    )
from project.cryptography.decryption import Decrypt    

class FollowingAPIView(viewsets.ModelViewSet):
    
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]
    serializer_class = FollowingSerializer

    def get_object(self, *args, **kwargs):
        user = None
        following = None
         
        try:            
            user_id = self.request.data.get('user')
            following_id = self.request.data.get('following')
            user = User.objects.get(id = user_id)          
            try:
                following = User.objects.get(id = following_id)
            except ObjectDoesNotExist:                
                user = None
            
        except ObjectDoesNotExist:
            following = None
        
        return user,following

    def get_queryset(self, *args, **kwargs):
        try:
            instance = Following.objects.get(user__username = self.kwargs.get('username'))
            return instance
        except ObjectDoesNotExist:
            return None
    
    def list(self, request, *args, **kwargs):
        instance = self.get_queryset(*args, **kwargs)
        if instance:
            serializer = self.get_serializer(instance=instance)          
            string_json_data = json_dumps(serializer.data)  
            data = Encrypt().encrypt(string_json_data)               
            original_data = json_loads(data = Decrypt().decrypt(data))
            print('sent data', original_data)
            return Response({'data' : data}, status=status.HTTP_200_OK)

        else:
            return Response({'data' : 'User does not follow to anyone'},status=status.HTTP_404_NOT_FOUND)

    def create(self, request, *args, **kwargs):
        serializer = FollowingSerializer(data=request.data) 
        
        serializer.is_valid(raise_exception=True)
        try:            
            user, following = self.get_object(*args, **kwargs)
          
            if user and following is not None:                 
                return self.perform_create(user,following,serializer)
        except:
            return Response({'data':'Not Found'},status=status.HTTP_404_NOT_FOUND)
    
    def perform_create(self, user, following, serializer):

        following_ = Following.objects.filter(user__id = user.id)
        print('ff',following)
        follower = Followers(following).get_object()
        print('follower',follower)
        following_obj = Following
        
        if following_:
             
            following_ = following_[0]        
                 
            if following not in following_.following.all():               
                
                update = Following().update(following_,following)
                
                follower_update = Follower().update(follower, user)
                serializer = FollowingSerializer(instance = update)
                string_json_data = json_dumps(serializer.data)        
                data = Encrypt().encrypt(string_json_data)      
                
                original_data = json_loads(data = Decrypt().decrypt(data))
                print('sent data', original_data)
                return Response({'data':data}, status=status.HTTP_200_OK)
            else:                  
                
                follower_remove = Follower().remove(follower, user)
                remove = Following().remove(following_, following)
                serializer = FollowingSerializer(instance=remove)
                string_json_data = json_dumps(serializer.data)        
                data = Encrypt().encrypt(string_json_data)      
                
                original_data = json_loads(data = Decrypt().decrypt(data))
                print('sent data', original_data)
                return Response({'data':data},status=status.HTTP_200_OK)
        else:         
            
            Following().create(Following, user, following)
            follower_update = Follower().update(follower, user)
            string_json_data = json_dumps(serializer.data)        
            data = Encrypt().encrypt(string_json_data)      
            
            original_data = json_loads(data = Decrypt().decrypt(data))
            print('sent data', original_data)
            return Response({'data':data},status=status.HTTP_201_CREATED)


            return Response({'data':data},status=status.HTTP_201_CREATED)


class Followers:

    def __init__(self, instance):
        self.instance = instance
    
    def get_object(self):
        user = self.instance
        followers, created = Follower.objects.get_or_create(user=user)

        return followers
    
class FollowersAPIView(viewsets.ModelViewSet):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]
    serializer_class = FollowerSerializer

    def get_queryset(self, *args, **kwargs):
        username = self.kwargs.get('username')
        
        try:
            follower_list = Follower.objects.get(user__username = username)
        except ObjectDoesNotExist:
            follower_list = None
        return follower_list
    
    def retrieve(self, request, *args, **kwargs):
        instance = self.get_queryset(*args, **kwargs)
       
        if instance:
            serializer = self.get_serializer(instance = instance)
            string_json_data = json_dumps(serializer.data)  
            data = Encrypt().encrypt(string_json_data)               
            original_data = json_loads(data = Decrypt().decrypt(data))
            print('sent data', original_data)
            return Response({'data' : data}, status=status.HTTP_200_OK)
        else:
            return Response({'data' : 'You dont have followers'},status=status.HTTP_404_NOT_FOUND)

