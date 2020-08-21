from .field_settings import SETTINGS_FIELDS
from django.test.signals import setting_changed
from project.utils.nested_settings import NestedSettings
from django.core.mail import send_mail

DEFAULTS = {f.name: f.default for f in SETTINGS_FIELDS}
IMPORT_STRINGS = [f.name for f in SETTINGS_FIELDS if f.import_string]


registration_settings = NestedSettings(
    None, DEFAULTS, IMPORT_STRINGS, root_setting_name = ''
)

def settings_changed_handler(*args, **kwargs):
    registration_settings.reset_settings()
    registration_settings.settings_attr_cache()

setting_changed.connect(settings_changed_handler)

 