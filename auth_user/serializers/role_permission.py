"""
RolePermissionSerializer
Serializer for both creating a Permission.
"""

from rest_framework import serializers

from utils.messages import error
from utils.exceptions import codes

from auth_user.constants import RoleEnum
from auth_user.db_access import permission_manager, role_permission_mapping_manager


class RolePermissionSerializer(serializers.Serializer):
    """
    Serializer for both creating a RolePermission.
    """

    permission_id = serializers.UUIDField()
    role_id = serializers.ChoiceField(choices=RoleEnum.choices, required=True)

    def validate(self, attrs):
        """
        Validate the input data for creating or updating a RolePermission.
        """

        if role_permission_mapping_manager.exists(
            {
                "role_id": attrs["role_id"],
                "permission_id": attrs["permission_id"],
            }
        ):
            raise serializers.ValidationError(
                {
                    "role_permission": error.ALREADY_EXIST,
                },
                code=codes.DUPLICATE_ENTRY,
            )

        return attrs

    def validate_permission_id(self, value):
        """
        Validate the permission_id field.
        """
        if not permission_manager.exists({"permission_id": value}):
            raise serializers.ValidationError(
                error.NO_DATA_FOUND,
                code=codes.NO_DATA_FOUND,
            )
        return value
