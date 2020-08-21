from django.conf import settings as root_settings
from rest_framework.settings import perform_import
class NestedSettings:

    def __init__(self, user_settings, defaults, import_strings, root_setting_name):
        if user_settings:
            self._user_settings = user_settings
        self.defaults = defaults
        self.import_strings = import_strings,
        self.root_settings_name = root_setting_name
    
    @property
    def user_settings(self):
        if not hasattr(self, '_user_settings'):
            self._user_settings = getattr(
                root_settings,
                self.root_settings_name,
                {}
            )
        return self.user_settings
    
    def reset_settings(self):
        if hasattr(self, '_user_settings'):
            del self._user_settings
    
    def settings_attr_cache(self):

        for attr in self.defaults.keys():
            if hasattr(self, key):
                delattr(self, key)