from copy import deepcopy

from celery_once.tasks import QueueOnce
from django.conf import settings

from applications.multi_tenant.db.database_alias import DatabaseAlias


class MultiTenantTask(QueueOnce):
    #: Enable argument checking.
    #: You can set this to false if you don't want the signature to be
    #: checked when calling the task.
    #: Set to false because we are attaching a tenant to the task
    #: and we don't want to check the signature.
    #: Defaults to :attr:`app.strict_typing <@Celery.strict_typing>`.
    typing = False

    once = {
        'graceful': True,
        'unlock_before_run': False
    }

    def __call__(self, *args, **kwargs):
        """
        Override the __call__ method to set the tenant name in the thread namespace.
        Args:
            *args:      args provided to the task
            **kwargs:   kwargs provided to the task

        Returns:    returns the result of the task

        """
        # Only clear the lock before the task's execution if the
        # "unlock_before_run" option is True
        if self.unlock_before_run():
            key = self.get_key(args, kwargs)
            self.once_backend.clear_lock(key)

        # Remove the tenant name from the kwargs so that the task signature
        # is not bound to the tenant name.
        tenant = kwargs.pop(settings.TENANT_KWARG)
        DatabaseAlias.set(tenant)

        return self.run(*args, **kwargs)

    def get_key(self, args=None, kwargs=None):
        key = super().get_key(args, kwargs)
        return f'{settings.REDIS_KEY_PREFIX}-{key}'

    def after_return(self, status, retval, task_id, args, kwargs, einfo):
        # Clear the tenant name from the thread namespace.
        DatabaseAlias.clear()
        super().after_return(status, retval, task_id, args, kwargs, einfo)

    def _get_call_args(self, args, kwargs):
        # QueueOnce._get_call_args validates the args and kwargs
        # by binding them to the task signature.
        # Since the settings.CELERY_BEAT_TENANT_KWARG_NAME
        # kwarg is not part of the signature,
        # we need to remove it from the kwargs before passing them
        # to QueueOnce._get_call_args.
        # Copy the kwargs so that we don't modify the original kwargs.
        _kwargs = deepcopy(kwargs)
        tenant = _kwargs.pop(settings.TENANT_KWARG)
        tenant_kwarg = {settings.TENANT_KWARG: tenant}
        task_call_args = super(MultiTenantTask, self)._get_call_args(args, _kwargs)

        # Add the tenant kwarg to the return value since this value is being
        # used to create the key for the lock.
        # We want to lock the task for the tenant that is running it.
        return task_call_args | tenant_kwarg
