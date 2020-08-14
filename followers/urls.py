from django.contrib import admin
from django.urls import path, include
from .apis import FollowersAPIView,CreateFollowerAPIView

urlpatterns = [
    path('followers/<user_id>/', FollowersAPIView.as_view({'get':'list'})),
    # path('follower/<pk>/', FollowerAPIView.as_view({'get' : 'retrieve'})),
    path('follower/<user_id>/<follower_id>/', CreateFollowerAPIView.as_view({'post':'create'})),

]