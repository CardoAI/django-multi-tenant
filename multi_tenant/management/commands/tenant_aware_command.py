from django.core.management import BaseCommand

from ...db import DatabaseAlias


class TenantAwareCommand(BaseCommand):
    """
    Base class for all tenant aware commands.
    The usage is like this:

    class MyCommand(TenantAwareCommand):
        def add_arguments(self, parser):
            super().add_arguments(parser)
            # add your own arguments here

        def handle(self, *args, **options):
            super().add_arguments(parser)
            # do something


    """

    def add_arguments(self, parser):
        """
        Add the database argument to the command. The database argument is
        required in a multi tenant environment.
        """
        parser.add_argument(
            "--database",
            action="store",
            dest="database",
        )

    def handle(self, *args, **options):
        """
        Get the database alias from the command line arguments and set it as
        the current database using DatabaseAlias.set().
        Args:
            *args:  The positional arguments.
            **options:  The keyword arguments.

        """
        database = options["database"]
        DatabaseAlias.set(database)
        self.stdout.write(f"Executing command for tenant {database}")
