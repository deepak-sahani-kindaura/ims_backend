from rest_framework import serializers

from utils.messages import error
from utils.exceptions import codes

from base.serializers.query import QuerySerializer

from tenant.db_access import tenant_manager

from auth_user.constants import RoleEnum


class UserListQuerySerializer(QuerySerializer, serializers.Serializer):
    first_name = serializers.CharField()
    last_name = serializers.CharField()


class UserCompanyAdminListQuerySerializer(
    UserListQuerySerializer,
    serializers.Serializer,
):
    tenant_id = serializers.UUIDField(required=True)
    role_id = serializers.ChoiceField(
        choices=RoleEnum.choices,
        default=RoleEnum.COMPANY_ADMIN,
    )

    def to_internal_value(self, data):
        data = data.copy()
        tenant_id = data.get("tenant_id")

        if not tenant_id:
            data["tenant_id"] = None

        data["role_id"] = RoleEnum.COMPANY_ADMIN

        data = QuerySerializer.to_internal_value(self, data)

        return data

    def validate_tenant_id(self, value):
        """
        Validates the tenant_id field.
        """

        if not tenant_manager.exists(query={"tenant_id": value}):
            raise serializers.ValidationError(
                error.NO_DATA_FOUND,
                code=codes.NO_DATA_FOUND,
            )

        return value
