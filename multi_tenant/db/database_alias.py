import logging
import sys
from contextlib import ContextDecorator
from threading import local
from typing import Optional

logger = logging.getLogger(__name__)
thread_namespace = local()


class DatabaseAlias(ContextDecorator):
    """
    Context manager that sets the current database alias.
    This class can be used in several ways:
    1. As a context manager:
        with DatabaseAlias('db_name'):
            # do something

    2. As a decorator:
        @DatabaseAlias('db_name')
        def some_function():
            # do something

    3. Directly using static methods:
        DatabaseAlias.set('db_name')
        # do something
        DatabaseAlias.clear()
    """
    field_name = 'database_alias'

    def __init__(self, alias: str):
        self.alias = alias

    def __enter__(self):
        DatabaseAlias.set(self.alias)

    def __exit__(self, exc_type, exc_val, exc_tb):
        DatabaseAlias.clear()

    @staticmethod
    def is_set() -> bool:
        return hasattr(thread_namespace, DatabaseAlias.field_name)

    @staticmethod
    def get() -> Optional[str]:
        if DatabaseAlias.is_set():
            return getattr(thread_namespace, DatabaseAlias.field_name)

    @staticmethod
    def set(alias):
        if DatabaseAlias.is_set():
            # If the database alias is already set, we do not allow to set it
            # again unless it is the same alias.
            # This is to prevent the database alias to be set to a different
            # value in the same thread.
            # A request-response cycle is required to set the database alias
            # only once and operate on the same database in its lifecycle.
            # The same applies to a single task, it is not allowed to set the
            # database alias in the same task to a different value.
            if DatabaseAlias.get() != alias:
                logger.error('ERROR: DATABASE ALIAS ALREADY SET')
                logger.error(f'Current db alias: {DatabaseAlias.get()}, new alias: {alias}')
                return sys.exit(1)

            else:
                # Normally in a request-response cycle, or a single task, the
                # database alias is set only once. But there is an exception
                # for the migrate command, which sets the database alias
                # multiple times to the same value.
                logger.info('Database alias already set to %s', alias)
                return

        setattr(thread_namespace, DatabaseAlias.field_name, alias)
        logger.info(f'Database alias switched to {alias}')

    @staticmethod
    def clear():
        if DatabaseAlias.is_set():
            delattr(thread_namespace, DatabaseAlias.field_name)
            logger.info('Database alias cleared')
