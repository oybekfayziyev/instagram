from .serializers import PostSerializer, PostRetrieveSerializer
from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework import status
from django.core.exceptions import ObjectDoesNotExist
from rest_framework.permissions import IsAdminUser, IsAuthenticatedOrReadOnly, IsAuthenticated
from rest_framework.authentication import TokenAuthentication
from .models import Post
from project.cryptography.encryption import (Encrypt, 
                                        json_dumps,
                                        json_loads
                                    )
from project.cryptography.decryption import Decrypt

class PostViewset(viewsets.ModelViewSet):    
    # queryset = Post 
    authentication_classes = [TokenAuthentication]
    serializer_class = PostSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]

    def get_queryset(self):
        post = Post.objects.all()
        return post 
    
    def list(self, request, *args, **kwargs):
        instance = self.get_queryset()
        serializer = self.get_serializer(instance = instance,many=True)         
        string_json_data = json_dumps(serializer.data)        
        data = Encrypt().encrypt(string_json_data)      
         
        original_data = json_loads(data = Decrypt().decrypt(data))
        print('sent data', original_data)
        return Response({'data' : data}, status=status.HTTP_200_OK)
    
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data) 
        serializer.is_valid(raise_exception=True) 
        self.perform_create(serializer)          
        headers = self.get_success_headers(serializer.data)
        string_json_data = json_dumps(serializer.data)        
        data = Encrypt().encrypt(string_json_data)       
        
        original_data = json_loads(data = Decrypt().decrypt(data))
        print('sent data', original_data)
        return Response({'data' : data}, status=status.HTTP_201_CREATED, headers=headers)
    
        
class PostDeleteViewset(viewsets.ViewSet):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def get_object(self,*args, **kwargs):
        try:            
            post = Post.objects.get(slug = kwargs.get('slug'))        
            return post 

        except ObjectDoesNotExist:
            return None
    
    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object(*args, **kwargs)
        serializer = self.get_serializer(instance)
        if instance:
            string_json_data = json_dumps(serializer.data)        
            data = Encrypt().encrypt(string_json_data) 
            original_data = json_loads(data = Decrypt().decrypt(data))
            print('sent data', original_data)
            return Response({'data':data}, status=status.HTTP_200_OK)

        return Response({'data' : 'Post slug is not found'},status=status.HTTP_404_NOT_FOUND)
    
    def get_serializer(self,instance,many=False):
        return PostRetrieveSerializer(instance=instance, many=many, context = {'request' : self.request})

    def remove(self, request, *args, **kwargs):
   
        instance = self.get_object(*args, **kwargs)
        if instance:
            
            if instance.user == request.user:
                self.perform_destroy(instance)
                return Response(status=status.HTTP_204_NO_CONTENT)
            return Response({'data' : 'You dont have permission delete this post'},status=status.HTTP_400_BAD_REQUEST)
        
        return Response({'data' : 'Post slug is not found'},status=status.HTTP_404_NOT_FOUND)

    def perform_destroy(self, instance):
        return instance.delete()