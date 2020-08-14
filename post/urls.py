from django.contrib import admin
from django.urls import path, include
from .apis import PostViewset, PostDeleteViewset

urlpatterns = [
    path('', PostViewset.as_view({'get':'list',
                                'post':'create',
                                })),
    path('<slug>', PostDeleteViewset.as_view({'delete':'remove',
                                            'get' : 'retrieve'})),    
]