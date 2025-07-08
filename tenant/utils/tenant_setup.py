"""
A class to handle the setup of a new tenant in the system.

"""

import copy

import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT

from django.core.management import call_command

from utils.messages import error
from utils.exceptions import exceptions, codes
from utils import settings, functions as comm_function

from tenant.constants import DatabaseStrategyEnum, DatabaseServerEnum
from tenant.db_access import tenant_manager, tenant_configuration_manager


class NewTenantSetup:
    """
    This class manages the database setup for new tenants, particularly handling
    different database strategies (shared vs separate databases) and performing
    necessary migrations.

    Args:
        tenant_config_obj: Configuration object containing tenant settings and properties.

    Attributes:
        tenant_config_obj: Stored tenant configuration object.
        DATABASES: Dictionary of database configurations loaded from settings.

    """

    def __init__(self, tenant_config_obj, request):
        self.request = request
        self.tenant_config_obj = tenant_config_obj

    def setup(self):
        """
        Sets up the database for a new tenant.
            - For shared database strategy, returns True without additional setup
            - For separate database strategy:
                * Creates a new database configuration
                * Names the database using tenant code
                * Runs database migrations
            Returns:
                bool: True if setup is successful
        """

        if self.tenant_config_obj.database_strategy == DatabaseStrategyEnum.SHARED:
            return True

        database_config = self.tenant_config_obj.database_config or {}

        database_name = database_config.get("database_name")

        if not database_name:

            tenant_obj = tenant_manager.get(
                query={"tenant_id": self.tenant_config_obj.tenant_id}
            )

            database_config["database_name"] = tenant_obj.tenant_code

            self.tenant_config_obj = tenant_configuration_manager.update(
                data={"database_config": database_config},
                query={
                    "tenant_configuration_id": self.tenant_config_obj.tenant_configuration_id
                },
            )

        set_database_to_global_settings(self.tenant_config_obj)

        kw = {}
        if comm_function.is_test():
            kw["verbosity"] = 0

        call_command(
            "migrate",
            database=database_config["database_name"],
            **kw,
        )

        return True


def set_database_to_global_settings(tenant_config_obj):
    """
    Configures and adds a new database configuration for a specific tenant to the global settings.
    """

    db_connection_code = tenant_config_obj.database_config["database_name"]

    DATABASES = settings.read("DATABASES")
    if db_connection_code in DATABASES:
        return True

    if tenant_config_obj.database_server == DatabaseServerEnum.SQLITE:
        return setup_sqlite(db_connection_code)

    if tenant_config_obj.database_server == DatabaseServerEnum.POSTGRES:
        return setup_postgres(tenant_config_obj)


def create_postgres_database(db_name, user, password, host="localhost", port="5432"):
    con = psycopg2.connect(
        dbname="postgres",  # connect to default 'postgres' DB
        user=user,
        password=password,
        host=host,
        port=port,
    )
    con.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
    cur = con.cursor()

    cur.execute("SELECT 1 FROM pg_database WHERE datname = %s;", (db_name,))
    exists = cur.fetchone()

    if not exists:
        cur.execute(f'CREATE DATABASE "{db_name}";')

    cur.close()
    con.close()

    return True


def setup_postgres(tenant_config_obj):

    database_config = tenant_config_obj.database_config

    create_postgres_database(
        host=database_config["host"],
        port=database_config["port"],
        user=database_config["username"],
        password=database_config["password"],
        db_name=database_config["database_name"],
    )

    DATABASES = settings.read("DATABASES")

    new_db = copy.deepcopy(DATABASES["default"])

    new_db["ENGINE"] = "django.db.backends.postgresql"

    new_db["HOST"] = database_config["host"]
    new_db["PORT"] = database_config["port"]
    new_db["USER"] = database_config["username"]
    new_db["PASSWORD"] = database_config["password"]
    new_db["NAME"] = database_config["database_name"]
    new_db["OPTIONS"] = database_config["options"] or {}

    DATABASES[database_config["database_name"]] = new_db

    return database_config["database_name"]


def setup_sqlite(db_connection_code):

    DATABASES = settings.read("DATABASES")

    new_db = copy.deepcopy(DATABASES["default"])

    new_db["NAME"] = f"{db_connection_code}.sqlite3"

    DATABASES[db_connection_code] = new_db

    return db_connection_code
