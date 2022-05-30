import logging
from typing import Callable

from django.conf import settings
from django.core.handlers.wsgi import WSGIRequest
from django.db.models.signals import pre_migrate, post_migrate
from django.dispatch import receiver
from django.http import HttpResponse

from applications.multi_tenant.db import DatabaseAlias

logger = logging.getLogger(__name__)


@receiver(pre_migrate)
def switch_database_pre_migrate(sender, **kwargs):
    database_alias = kwargs.get('using')
    DatabaseAlias.set(database_alias)


@receiver(post_migrate)
def switch_database_post_migrate(sender, **kwargs):
    DatabaseAlias.clear()


class ThreadLocalMiddleware:
    """
    Middleware that sets the thread local variable `database_alias`.
    This middleware must be placed before any other middleware that
    executes queries on the database.
    In this way, the database alias is set before any other middleware is
    called and it is removed after all of them are called.
    """

    def __init__(self, get_response: Callable):
        """
        Middleware initialization. Only called once per Django application initialization.
        Args:
            get_response: Callable to get the response of the view.
        """

        self.get_response = get_response

    def __call__(self, request: WSGIRequest) -> HttpResponse:
        """
        Called by Django for each http request to process it and return a response.
        Everything that should be done before the view is called is done before
        the get_response method is called and everything that should be done
        after the view is called is done after the get_response method is called.
        Args:
            request: Django request object.

        Returns:    HttpResponse object.

        """
        if DatabaseAlias.is_set():
            raise Exception('Database alias already set')

        database_alias = self._get_database_alias_from_header(request)
        self._save_to_thread_local(database_alias)

        # Call the next middleware in the chain until the response is returned.
        # After that, the database alias is removed from the thread local variable.
        response = self.get_response(request)
        DatabaseAlias.clear()

        return response

    @staticmethod
    def _get_database_alias_from_header(request):
        if settings.DATABASE_ALIAS_HEADER not in request.META:
            raise Exception('Database alias not found in request', request.META)

        return request.META[settings.DATABASE_ALIAS_HEADER]

    @staticmethod
    def _save_to_thread_local(database_alias: str):
        DatabaseAlias.set(database_alias)
