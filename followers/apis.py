from .serializers import FollowerSerializer
from rest_framework import viewsets
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.authentication import TokenAuthentication
from django.core.exceptions import ObjectDoesNotExist
from .models import Follower, User
from django.shortcuts import get_object_or_404
from django.utils import timezone
from rest_framework.response import Response
from project.cryptography.encryption import (Encrypt, 
                                        json_dumps,
                                        json_loads
                                    )
from project.cryptography.decryption import Decrypt                                   
class FollowersAPIView(viewsets.ModelViewSet):
    
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]
    serializer_class = FollowerSerializer

    def get_queryset(self, *args, **kwargs):
        try:
            instance = Follower.objects.get(user__id = self.kwargs.get('user_id'))
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
            return Response({'data' : 'You dont have followers'},status=status.HTTP_404_NOT_FOUND)

class CreateFollowerAPIView(viewsets.ViewSet):

    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]
    serializer_class = FollowerSerializer

    def get_object(self, *args, **kwargs):
        user = None
        follower = None
         
        try:                     
            user = User.objects.get(id = kwargs.get('user_id'))          
            try:
                follower = User.objects.get(id = kwargs.get('follower_id'))
            except ObjectDoesNotExist:                
                user = None
            
        except ObjectDoesNotExist:
            follower = None
        
        return user,follower
        
    def create(self, request, *args, **kwargs):
        serializer = FollowerSerializer(data=request.data) 
        
        serializer.is_valid(raise_exception=True)
        try:            
            user, follower = self.get_object(*args, **kwargs)
            
            if user and follower is not None:
                 
                return self.perform_create(user,follower)
        except:
            return Response({'data':'Not Found'},status=status.HTTP_404_NOT_FOUND)
    
    def perform_create(self, user, follower):

        follower_ = Follower.objects.filter(user__id = user.id)
        follower_obj = Follower()
        if follower_:
            follower_ = follower_[0]                   
            if follower not in follower_.followers.all():               
              
                follower_obj.update(follower_,follower)
                return Response({'data' : 'Follower list is updated'}, status=status.HTTP_200_OK)
            else:                  
               
                follower_obj.remove(follower_, follower)
                return Response({'data' : 'Follower removed'},status=status.HTTP_200_OK)
        else:          
            follower_obj.create(Follower, user, follower)
            
            return Response({'data' : 'Follower created'},status=status.HTTP_201_CREATED)
        
       