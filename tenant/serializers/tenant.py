"""
Serializer for Tenant.
"""

from rest_framework import serializers

from utils.messages import error
from utils.exceptions import codes
from utils.validators.unique import validate_unique

from tenant.db_access import tenant_manager
from tenant.constants import (
    AuthenticationTypeEnum,
    DatabaseStrategyEnum,
    DatabaseServerEnum,
)


class TenantSerializer(serializers.Serializer):
    """Serializer for the Tenant model"""

    tenant_code = serializers.CharField(max_length=256)
    tenant_name = serializers.CharField(max_length=256)

    def get_query(self, field_name, value):
        """
        Generate a query dictionary for tenant field validation.
        This method constructs a query dictionary used to check uniqueness of tenant fields.
        For updates, it excludes the current tenant instance from the uniqueness check.
        Args:
            field_name (str): The name of the field to query
            value: The value to check for uniqueness
        Returns:
            dict: Query dictionary containing field name and value,
            with optional tenant_id exclusion for updates
        """

        is_update = self.instance is not None

        query = {field_name: value}
        if is_update:
            query["tenant_id"] = {"NOT": self.instance.tenant_id}

        return query

    def validate_tenant_code(self, value):
        """
        Validate tenant_code field.
        - For create: tenant_code must not exist.
        - For update: tenant_code must not belong to a different tenant.
        """

        validate_unique(tenant_manager, self.get_query("tenant_code", value))

        return value

    def validate_tenant_name(self, value):
        """
        Validate tenant_name field.
        - For create: tenant_name must not exist.
        - For update: tenant_name must not belong to a different tenant.
        """

        validate_unique(tenant_manager, self.get_query("tenant_name", value))

        return value


class DatabaseConfigSerializer(serializers.Serializer):
    password = serializers.CharField(required=True)
    username = serializers.CharField(required=True)

    host = serializers.CharField(required=True)
    port = serializers.IntegerField(required=True)
    options = serializers.JSONField(required=False, allow_null=True, default=None)
    database_name = serializers.CharField(required=False, allow_null=True, default=None)


class TenantConfigurationSerializer(serializers.Serializer):
    """Serializer for Tenant Configuration"""

    authentication_type = serializers.ChoiceField(
        choices=AuthenticationTypeEnum.choices
    )

    database_strategy = serializers.ChoiceField(
        default=DatabaseStrategyEnum.SHARED,
        choices=DatabaseStrategyEnum.choices,
    )

    database_server = serializers.ChoiceField(
        default=DatabaseServerEnum.SQLITE,
        choices=DatabaseServerEnum.choices,
    )

    database_config = DatabaseConfigSerializer(
        required=False, default=None, allow_null=True
    )

    tenant_id = serializers.UUIDField()

    def validate(self, attrs):
        """
        Validates the database strategy and server combination for tenant configuration.
        Ensures that if the database strategy is set to SHARED, the database server must be SQLITE.
        Raises a ValidationError if the combination is invalid.
        """

        database_server = attrs["database_server"]
        database_strategy = attrs["database_strategy"]

        if database_strategy == DatabaseStrategyEnum.SHARED:
            if database_server != DatabaseServerEnum.SQLITE:
                raise serializers.ValidationError(
                    {"database_server": error.CANNOT_CHANGE_DB_STRATEGY},
                    code=codes.INVALID_CHOICE,
                )

        else:
            if database_server != DatabaseServerEnum.SQLITE:
                if not attrs.get("database_config"):
                    raise serializers.ValidationError(
                        {"database_config": self.error_messages["required"]},
                        code=codes.REQUIRED,
                    )
        return attrs

    def validate_tenant_id(self, value):
        """
        Validate that the provided tenant_id exists in the tenant manager.
        """
        if not tenant_manager.exists({"tenant_id": value}):
            raise serializers.ValidationError(
                error.NO_DATA_FOUND,
                code=codes.NO_DATA_FOUND,
            )

        return value
