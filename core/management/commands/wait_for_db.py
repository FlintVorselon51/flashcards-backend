import time
from django.core.management.base import BaseCommand
from django.db import connections
from django.db.utils import OperationalError


class Command(BaseCommand):
    def handle(self, *args, **options):
        self.stdout.write('Waiting for database...')
        db_conn = None
        max_retries = 30
        retry_delay = 1

        for i in range(max_retries):
            try:
                db_conn = connections['default']
                db_conn.ensure_connection()
                self.stdout.write(self.style.SUCCESS('Database available!'))
                return
            except OperationalError:
                self.stdout.write(f'Database unavailable, waiting {retry_delay} second... ({i + 1}/{max_retries})')
                time.sleep(retry_delay)

        self.stdout.write(self.style.ERROR('Could not connect to database'))
        exit(1)
