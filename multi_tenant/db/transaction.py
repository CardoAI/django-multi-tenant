from django.db.transaction import Atomic

from .database_alias import DatabaseAlias


class TenantAtomic(Atomic):
    """
    A transaction that can be used in a multi-tenant application.
    This transaction is bound to the current tenant.
    The default implementation is to use the default database.
    We want to override this by using the tenant database alias instead.
    """

    def __enter__(self):
        self.using = DatabaseAlias.get()
        super().__enter__()


def tenant_atomic(using=None, savepoint=True):
    # Bare decorator: @atomic -- although the first argument is called
    # `using`, it's actually the function being decorated.
    if callable(using):
        return TenantAtomic(using=None, savepoint=savepoint)(using)
    # Decorator: @atomic(...) or context manager: with atomic(...): ...
    else:
        return TenantAtomic(using, savepoint)
