from typing import Type

from django.db import connections, models

from .database_alias import DatabaseAlias


def get_connection(database_alias: str = None):
    """
    Get the connection to the database with the given alias or the default one.
    Default value will be retrieved from DatabaseAlias.get()
    This uses the connections dict from django.db to get the required connection.

    The default implementation of this function uses the 'default' alias
    if not argument is given. We want to use the DatabaseAlias class to
    determine the correct alias.
    Args:
        database_alias: Name of the database alias

    Returns:    The connection to the database

    """
    database_alias = database_alias or DatabaseAlias.get()
    connection = connections[database_alias]

    return connection


def get_fields_from_model(model: Type[models.Model], field_type) -> list:
    """
    Get all fields from a given model which are of the given type.

    Args:
        model:       Model from which we will get the fields
        field_type:  Type of the fields we want to get

    Returns:
        fields:      List of fields of the given type

    """
    fields = []
    for field in model._meta.get_fields():
        if isinstance(field, field_type):
            fields.append(field)

    return fields


def count_db_queries() -> int:
    """
    Count number of db queries to the actual db connection.

    By default, Django will only count the queries issued to the
    default database connection, which is always zero for Mercury,
    because we use are always connected to a tenant database.
    """
    return len(get_connection().queries)
