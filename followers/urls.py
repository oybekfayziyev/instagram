from django.contrib import admin
from django.urls import path, include
from .apis import (FollowingAPIView,
        FollowersAPIView
    )

urlpatterns = [
    path('<username>/following/', FollowingAPIView.as_view({'get':'list','post':'create'})), 
    # path('<username>/following/', CreateFollowingAPIView.as_view({'post':'create'})),
    # Followers
    path('<username>/followers/', FollowersAPIView.as_view({'get':'retrieve'})),



]