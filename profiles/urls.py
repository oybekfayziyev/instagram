from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from .apis import LogoutApi, RegisterViewSet
from rest_framework.authtoken import views as token_views
from .apis import ( reset_password_request_token, 
        reset_password_validate_token, 
        reset_password_confirm,
        verification_viewset,
        verification_by_verify
)

urlpatterns = [
    # path('accounts/', include('rest_registration.api.urls')),
    # path('accounts/login/', LoginViewSet.as_view({'post':'create'})),
    path('accounts/login/', token_views.obtain_auth_token),   # TOKEN AUTHENTICATION
    path('accounts/logout/', LogoutApi.as_view()),
    path('accounts/register/', RegisterViewSet.as_view({'post':'create'})),


    # RESET PASSWORD
    path('reset-password/validate_token/', reset_password_validate_token, name="reset-password-validate"),
    path('reset-password/confirm/<token>/', reset_password_confirm, name="reset-password-confirm"),
    path('reset-password/', reset_password_request_token, name="reset-password-request"),

    # SEND SMS 
    path('send/sms/', verification_viewset),
    path('send/sms/verify/',verification_by_verify),
    
] 
