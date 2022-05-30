from django.conf import settings
from django.core.management import BaseCommand
from django.core.management import call_command


# todo: make this to run in parallel
class Command(BaseCommand):

    def handle(self, *args, **options):
        databases = settings.MIGRATE_DATABASES
        for db in databases:
            self.stdout.write(f'Migrating database: {db}')
            try:
                call_command('migrate', database=db)
            except Exception as e:
                self.stderr.write(f'Failed to migrate database: {e}')
