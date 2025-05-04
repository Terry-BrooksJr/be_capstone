from drf_spectacular.extensions import OpenApiAuthenticationExtension

class DjsoerAuthenticationScheme(OpenApiAuthenticationExtension):
    target_class = 'my_app.MyAuthentication'  # full import path OR class ref
    name = 'TokenAuth'  # name used in the schema

    def get_security_definition(self, auto_schema):
        return {
            'type': 'apiKey',
            'in': 'header',
            'name': 'api_key',
        }
