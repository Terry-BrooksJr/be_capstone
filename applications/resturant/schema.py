from drf_spectacular.extensions import OpenApiAuthenticationExtension
from drf_spectacular.plumbing import build_bearer_security_scheme_object


class DjsoerAuthenticationScheme(OpenApiAuthenticationExtension):
    target_class = "my_app.MyAuthentication"  # full import path OR class ref
    name = "TokenAuth"  # name used in the schema

    def get_security_definition(self, auto_schema):
        return build_bearer_security_scheme_object(
            header_name='Authorization',
            token_prefix=self.target.keyword,
        )
        