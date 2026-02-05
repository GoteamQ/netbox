from django.db import models
from django.urls import reverse
from django.core.validators import MinLengthValidator

from netbox.models import NetBoxModel


class GCPOrganization(NetBoxModel):
    name = models.CharField(max_length=255, help_text='Display name for this GCP organization')
    organization_id = models.CharField(
        max_length=50, unique=True, validators=[MinLengthValidator(1)], help_text='GCP Organization ID (numeric)'
    )
    service_account_json = models.TextField(help_text='Service account JSON key content for API authentication')
    is_active = models.BooleanField(default=True, help_text='Enable/disable discovery for this organization')
    last_discovery = models.DateTimeField(null=True, blank=True, help_text='Last successful discovery timestamp')
    discovery_status = models.CharField(
        max_length=50,
        default='pending',
        choices=[
            ('pending', 'Pending'),
            ('running', 'Running'),
            ('canceling', 'Canceling'),
            ('canceled', 'Canceled'),
            ('completed', 'Completed'),
            ('failed', 'Failed'),
        ],
    )
    cancel_requested = models.BooleanField(default=False, help_text='Cancel the current discovery run')
    discovery_error = models.TextField(blank=True, help_text='Last discovery error message if any')
    auto_discover = models.BooleanField(default=False, help_text='Automatically discover assets on schedule')
    discover_compute = models.BooleanField(default=True, help_text='Discover Compute Engine resources')
    discover_networking = models.BooleanField(default=True, help_text='Discover VPC and networking resources')
    discover_databases = models.BooleanField(default=True, help_text='Discover Cloud SQL and database resources')
    discover_storage = models.BooleanField(default=True, help_text='Discover Cloud Storage resources')
    discover_kubernetes = models.BooleanField(default=True, help_text='Discover GKE clusters')
    discover_serverless = models.BooleanField(default=True, help_text='Discover Cloud Functions and Cloud Run')
    discover_iam = models.BooleanField(default=True, help_text='Discover IAM resources')

    class Meta:
        ordering = ['name']
        verbose_name = 'GCP Organization'
        verbose_name_plural = 'GCP Organizations'

    def __str__(self):
        return f'{self.name} ({self.organization_id})'

    def get_absolute_url(self):
        return reverse('gcp:gcporganization', args=[self.pk])

    def get_service_account_info(self):
        import json

        try:
            return json.loads(self.service_account_json)
        except json.JSONDecodeError:
            return None


class DiscoveryLog(NetBoxModel):
    organization = models.ForeignKey(GCPOrganization, on_delete=models.CASCADE, related_name='discovery_logs')
    started_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    status = models.CharField(
        max_length=50,
        default='running',
        choices=[
            ('running', 'Running'),
            ('canceled', 'Canceled'),
            ('completed', 'Completed'),
            ('failed', 'Failed'),
        ],
    )
    projects_discovered = models.IntegerField(default=0)
    instances_discovered = models.IntegerField(default=0)
    networks_discovered = models.IntegerField(default=0)
    databases_discovered = models.IntegerField(default=0)
    buckets_discovered = models.IntegerField(default=0)
    clusters_discovered = models.IntegerField(default=0)
    total_resources = models.IntegerField(default=0)
    error_message = models.TextField(blank=True)
    log_output = models.TextField(blank=True)

    class Meta:
        ordering = ['-started_at']
        verbose_name = 'Discovery Log'
        verbose_name_plural = 'Discovery Logs'

    def __str__(self):
        return f'Discovery {self.organization.name} - {self.started_at}'

    def get_absolute_url(self):
        return reverse('gcp:discoverylog', args=[self.pk])
