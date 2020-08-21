from django.contrib import admin
from .models import Profile, ResetPasswordToken,SMSVerification
from django.utils.html import format_html

# Register your models here.

admin.site.register(ResetPasswordToken)
class ResetPasswordTokenAdmin(admin.ModelAdmin):
    list_display = ('user', 'key', 'created_at', 'ip_address', 'user_agent')



class ProfileAdmin(admin.ModelAdmin):

    def image_tag(self, obj):
        return format_html('<img src={} height="50px" width="50px"/>'.format(obj.profile_pic.url))
		
    
    image_tag.short_description = 'Image'

    list_display = ['user','first_name','last_name','profile_pic']

admin.site.register(Profile,ProfileAdmin)

admin.site.register(SMSVerification)
class SMSVerificationAdmin(admin.ModelAdmin):
    list_display = ("id", "security_code", "phone_number", "is_verified", "created_at")
    search_fields = ("phone_number",)
    ordering = ("phone_number",)
    readonly_fields = (
        "security_code",
        "phone_number",
        "session_token",
        "is_verified",
        "created_at",
        "modified_at",
    )
