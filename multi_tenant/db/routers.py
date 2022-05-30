from .database_alias import DatabaseAlias


class MultiTenantRouter:

    @staticmethod
    def db_for_read(model, **hints):
        return DatabaseAlias.get()

    @staticmethod
    def db_for_write(model, **hints):
        return DatabaseAlias.get()
