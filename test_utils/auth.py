import secrets

from auth_user.constants import RoleEnum
from auth_user.db_access import user_manager, token_manager


def create_super_admin_test_user():
    """
    Logs in a user via API and returns an authenticated APIClient.
    """

    _user_manager = user_manager.disable_tenant_aware()
    user = _user_manager.upsert(
        data={
            "last_name": "Sahni",
            "first_name": "Deepak",
            "phone_number": "9878786565",
            "role_id": RoleEnum.SUPER_ADMIN,
            "email": "test.super.admin@gmail.com",
        },
        query={"email": "test.super.admin@gmail.com"},
    )

    user.set_password("1234")
    user.save()

    return user.to_dict()


def create_super_admin_test_token():

    _token_manager = token_manager.disable_tenant_aware()

    user = create_super_admin_test_user()
    token = _token_manager.disable_tenant_aware().upsert(
        {
            "user_id": user["user_id"],
            "token": secrets.token_hex(5),
        },
        query={
            "user_id": user["user_id"],
        },
    )

    return token.to_dict()
