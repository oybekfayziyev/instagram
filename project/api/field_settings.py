from collections import namedtuple, OrderedDict
from textwrap import dedent
_Field = namedtuple('_Field', [
    'name',
    'default',
    'help',
    'import_string'
])

class Field(_Field):

    def __new__(
            cls, name, *,
            default=None,
            help=None,  # pylint: disable=redefined-builtin
            import_string=False):
        return super().__new__(
            cls, name=name, default=default,
            help=help, import_string=import_string)
    

LOGIN_SETTINGS_FIELD = [
    Field(
        'LOGIN_SERIALIZER_CLASS',
        default = 'serializers.DefaulLoginSerializer',
        import_string = True
    ),

    Field('LOGIN_RETRIEVE_TOKEN'),
    Field('LOGIN_AUTHENTICATE_SESSION'),

    Field(
        'AUTH_TOKEN_MANAGER_CLASS',
        default='profiles.auth_token_managers.RestFrameworkAuthTokenManager',  # noqa: E501
        import_string=True,
        help=dedent("""\
            The token manager class used by :ref:`login-view`
            and :ref:`logout-view` which provides an interface for providing
            and optionally revoking the token.
            The class should inherit from
            ``rest_registration.token_managers.AbstractTokenManager``.
            """)
    ),
]

PERMISSION_SETTINGS_FIELD = [
    Field(
        'NOT_AUTHENTICATED_PERMISSION_CLASSES',
        default = ['rest_framework.permissions.AllowAny'],
        import_string = True,

    )
]


SETTINGS_FIELDS_GROUP_MAP = OrderedDict([
    ('login', LOGIN_SETTINGS_FIELD),
])

SETTINGS_FIELDS_GROUP = list(SETTINGS_FIELDS_GROUP_MAP.values())
SETTINGS_FIELDS = [f for fields in SETTINGS_FIELDS_GROUP for f in fields]