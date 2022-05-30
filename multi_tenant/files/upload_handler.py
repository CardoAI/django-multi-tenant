import os

from django.conf import settings
from django.utils.deconstruct import deconstructible


@deconstructible
class UploadPath:
    """
    This is required to have an isolation between the files uploaded by
    different tenants. The isolation is achieved by creating a folder
    with the name of the tenant in the MEDIA_ROOT.

    Construct a path to a file based on the folder name and tenant name.
    upload_to is a keyword argument for the FileField.
    It accepts a string or a callable which should return a string when called.
    The callable is called every time the file is saved with arguments:
    instance - the model instance that is being saved
    filename - the name of the file that is being saved

    We will use the tenant name, folder name if given, and the file name to
    construct the path. The path will be constructed as follows:
    tenant/folder/filename
    Args:
        folder: The folder name to use. if None, upload to tenant folder directly.

    Returns:
        A string representing the path to the file prefixed by tenant and folder name.

    """

    def __init__(self, folder=None):
        self.folder = folder or ''

    def __call__(self, instance, filename):
        tenant = instance._state.db
        other_tenant_names = set(settings.DATABASES.keys()) - {'default', tenant}

        if not tenant:
            raise ValueError(f'Tenant name is not set when saving a file.'
                             f'Instance: {instance}, filename: {filename}')

        if filename and tenant not in filename:
            # Validate if one of the tenants is not already prefixed to the file.
            if any(tenant_name in filename for tenant_name in other_tenant_names):
                raise ValueError(f'[upload_to_folder]: '
                                 f'A tenant is already set for this file.'
                                 f'{instance=} {tenant=}')

            return os.path.join(tenant, self.folder, filename)


upload_to_folder = UploadPath
