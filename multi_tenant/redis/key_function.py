from ..db import DatabaseAlias
from ...common.utils import push_to_sentry, SENTRY_EVENT_LEVEL


def make_key(key, key_prefix, version):
    if not DatabaseAlias.is_set():
        push_to_sentry(
            message=f'DatabaseAlias is not set when calling make_key',
            level=SENTRY_EVENT_LEVEL.error,
            tag_name='redis_key_function',
            tag_value='make_key',
            extra={
                'key': key,
                'key_prefix': key_prefix,
                'version': version
            }
        )

    return ':'.join([DatabaseAlias.get(), key_prefix, str(version), key])
