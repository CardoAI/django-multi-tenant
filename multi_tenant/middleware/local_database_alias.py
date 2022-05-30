from django.conf import settings
from django.core.exceptions import MiddlewareNotUsed


class LocalDatabaseAliasMiddleware:
    """
    This middleware is used to set the database alias to the local database
    when we are running in Debug mode.
    The default implementation requires a database alias to be set in the
    request headers (e.g. X-Database-Alias). This is not practical in
    a development environment, so we use this middleware to set the database
    alias to the local database. The value of the alias is set in the
    settings.py file (DEVELOPMENT_DATABASE_ALIAS).
    """

    def __init__(self, get_response):
        if not settings.DEBUG:
            raise MiddlewareNotUsed()

        self.get_response = get_response

    def __call__(self, request):
        request.META[settings.DATABASE_ALIAS_HEADER] = settings.DEVELOPMENT_DATABASE_ALIAS
        return self.get_response(request)
