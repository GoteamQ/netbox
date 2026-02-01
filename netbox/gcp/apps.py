import os
import sys

from django.apps import AppConfig


class GCPConfig(AppConfig):
    name = 'gcp'
    verbose_name = 'Google Cloud Platform'

    def ready(self):
        from netbox.models.features import register_models

        register_models(*self.get_models())

        if not self._should_cleanup_on_startup():
            return

        self._cleanup_stale_discovery()

    def _should_cleanup_on_startup(self):
        if os.getenv('GCP_CLEANUP_ON_STARTUP', 'true').lower() not in {'1', 'true', 'yes', 'on'}:
            return False

        blocked_commands = {
            'makemigrations',
            'migrate',
            'collectstatic',
            'shell',
            'dbshell',
            'loaddata',
            'dumpdata',
        }
        return not any(cmd in sys.argv for cmd in blocked_commands)

    def _cleanup_stale_discovery(self):
        try:
            from django.db import connection
            from django.utils import timezone
            from django_rq import get_queue
            from rq.registry import (
                StartedJobRegistry,
                FailedJobRegistry,
                DeferredJobRegistry,
                FinishedJobRegistry,
                ScheduledJobRegistry,
            )

            with connection.cursor() as cursor:
                tables = {name.lower() for name in connection.introspection.table_names(cursor)}

            if 'gcp_gcporganization' not in tables or 'gcp_discoverylog' not in tables:
                return

            from .models import GCPOrganization, DiscoveryLog

            queues = ['high', 'default', 'low']
            for name in queues:
                q = get_queue(name)
                q.empty()
                StartedJobRegistry(name, q.connection).cleanup()
                FailedJobRegistry(name, q.connection).cleanup()
                DeferredJobRegistry(name, q.connection).cleanup()
                FinishedJobRegistry(name, q.connection).cleanup()
                ScheduledJobRegistry(name, q.connection).cleanup()

            GCPOrganization.objects.filter(discovery_status__in=['running', 'canceling']).update(
                discovery_status='failed',
                discovery_error='Stale task reset',
                cancel_requested=False,
            )
            DiscoveryLog.objects.filter(status='running').update(
                status='failed',
                completed_at=timezone.now(),
                error_message='Stale task reset',
            )
        except Exception:
            # Avoid crashing app startup if cleanup fails
            return
