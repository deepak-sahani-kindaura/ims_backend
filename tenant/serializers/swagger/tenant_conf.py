"""
Tenant Configuration Serializer and Swagger Examples
"""

from rest_framework import serializers
from drf_spectacular.utils import OpenApiExample
from utils.swagger.common_swagger_functions import (
    get_create_success_example,
    get_by_id_success_example,
)
from tenant.constants import (
    AuthenticationTypeEnum,
    DatabaseStrategyEnum,
    DatabaseServerEnum,
)


# ----------------------------------
# Serializers
# ----------------------------------


class DatabaseConfigSerializer(serializers.Serializer):
    password = serializers.CharField(required=True)
    username = serializers.CharField(required=True)

    host = serializers.CharField(required=True)
    port = serializers.IntegerField(required=True)
    options = serializers.JSONField(required=False, allow_null=True, default=None)
    database_name = serializers.CharField(required=False, allow_null=True, default=None)


class TenantConfigurationDataSerializer(serializers.Serializer):
    """
    Serializer for creating and updating tenant configuration.
    """

    authentication_type = serializers.ChoiceField(
        choices=AuthenticationTypeEnum.choices,
        help_text="Authentication type (e.g., password, SAML, OIDC).",
    )
    database_strategy = serializers.ChoiceField(
        choices=DatabaseStrategyEnum.choices,
        default=DatabaseStrategyEnum.SHARED,
        help_text="Database Strategy type (e.g., Shared DB, Separate DB).",
    )
    database_server = serializers.ChoiceField(
        choices=DatabaseServerEnum.choices,
        default=DatabaseServerEnum.SQLITE,
        help_text="Choose the Database server (e.g., Sqlite3, PostgresDB, MySQL DB).",
    )
    database_config = DatabaseConfigSerializer(required=False)


class TenantConfigurationResponseSerializer(serializers.Serializer):
    """
    Serializer for the response of tenant configuration endpoints.
    """

    data = TenantConfigurationDataSerializer(
        help_text="Tenant configuration information."
    )
    errors = serializers.JSONField(
        help_text="Any errors message for the response.", allow_null=True
    )
    messages = serializers.JSONField(
        help_text="Any informational messages for the response body.", allow_null=True
    )
    status_code = serializers.IntegerField(default=200)
    is_success = serializers.BooleanField(default=True)


# ----------------------------------
# Swagger Examples
# ----------------------------------

tenant_config_sample_data = {
    "database_strategy": DatabaseStrategyEnum.SHARED.name,
    "authentication_type": AuthenticationTypeEnum.JWT_TOKEN.name,
    "database_server": DatabaseServerEnum.SQLITE.name,
    "database_config": {
        "username": "tenant_user",
        "password": "secure_password",
        "host": "localhost",
        "port": 5432,
        "database_name": "tenant_db",
        "options": None,
    },
}

tenant_config_create_success_example: OpenApiExample = get_create_success_example(
    name="Create Tenant Configuration - Success",
    data=tenant_config_sample_data,
)

tenant_config_get_by_id_success_example: OpenApiExample = get_by_id_success_example(
    name="Get Tenant Configuration by Id - Success",
    data=tenant_config_sample_data,
)
