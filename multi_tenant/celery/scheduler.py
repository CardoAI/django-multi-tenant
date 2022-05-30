from celery.utils.log import get_logger
from django.conf import settings
from django.db import close_old_connections, transaction
from django_celery_beat.schedulers import DatabaseScheduler
from django.db.utils import DatabaseError, InterfaceError

logger = get_logger(__name__)
debug, info, warning = logger.debug, logger.info, logger.warning


class MultiTenantDatabaseScheduler(DatabaseScheduler):

    def schedule_changed(self):
        try:
            close_old_connections()

            # If MySQL is running with transaction isolation level
            # REPEATABLE-READ (default), then we won't see changes done by
            # other transactions until the current transaction is
            # committed (Issue #41).
            try:
                transaction.commit(using=settings.DJANGO_CELERY_BEAT_DB_ALIAS)
            except transaction.TransactionManagementError:
                pass  # not in transaction management.

            last, ts = self._last_timestamp, self.Changes.last_change()
        except DatabaseError as exc:
            logger.exception('Database gave error: %r', exc)
            return False
        except InterfaceError:
            warning(
                'DatabaseScheduler: InterfaceError in schedule_changed(), '
                'waiting to retry in next call...'
            )
            return False

        try:
            if ts and ts > (last if last else ts):
                return True
        finally:
            self._last_timestamp = ts
        return False
