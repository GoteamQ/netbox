from django.db import migrations, models
import django.db.models.deletion
import taggit.managers
import utilities.json


class Migration(migrations.Migration):

    dependencies = [
        ('extras', '0001_initial'),
        ('gcp', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='GCPOrganization',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False)),
                ('created', models.DateTimeField(auto_now_add=True, null=True)),
                ('last_updated', models.DateTimeField(auto_now=True, null=True)),
                ('custom_field_data', models.JSONField(blank=True, default=dict, encoder=utilities.json.CustomFieldJSONEncoder)),
                ('name', models.CharField(max_length=255)),
                ('organization_id', models.CharField(max_length=50, unique=True)),
                ('service_account_json', models.TextField(blank=True)),
                ('is_active', models.BooleanField(default=True)),
                ('auto_discover', models.BooleanField(default=False)),
                ('discover_compute', models.BooleanField(default=True)),
                ('discover_networking', models.BooleanField(default=True)),
                ('discover_databases', models.BooleanField(default=True)),
                ('discover_storage', models.BooleanField(default=True)),
                ('discover_kubernetes', models.BooleanField(default=True)),
                ('discover_serverless', models.BooleanField(default=True)),
                ('discover_iam', models.BooleanField(default=True)),
                ('discovery_status', models.CharField(default='pending', max_length=20)),
                ('last_discovery', models.DateTimeField(blank=True, null=True)),
                ('discovery_error', models.TextField(blank=True)),
                ('tags', taggit.managers.TaggableManager(through='extras.TaggedItem', to='extras.Tag')),
            ],
            options={
                'verbose_name': 'GCP Organization',
                'verbose_name_plural': 'GCP Organizations',
                'ordering': ['name'],
            },
        ),
        migrations.CreateModel(
            name='DiscoveryLog',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False)),
                ('created', models.DateTimeField(auto_now_add=True, null=True)),
                ('last_updated', models.DateTimeField(auto_now=True, null=True)),
                ('custom_field_data', models.JSONField(blank=True, default=dict, encoder=utilities.json.CustomFieldJSONEncoder)),
                ('started_at', models.DateTimeField(auto_now_add=True)),
                ('completed_at', models.DateTimeField(blank=True, null=True)),
                ('status', models.CharField(default='running', max_length=20)),
                ('projects_discovered', models.IntegerField(default=0)),
                ('instances_discovered', models.IntegerField(default=0)),
                ('networks_discovered', models.IntegerField(default=0)),
                ('databases_discovered', models.IntegerField(default=0)),
                ('buckets_discovered', models.IntegerField(default=0)),
                ('clusters_discovered', models.IntegerField(default=0)),
                ('total_resources', models.IntegerField(default=0)),
                ('error_message', models.TextField(blank=True)),
                ('log_output', models.TextField(blank=True)),
                ('organization', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='discovery_logs', to='gcp.gcporganization')),
                ('tags', taggit.managers.TaggableManager(through='extras.TaggedItem', to='extras.Tag')),
            ],
            options={
                'verbose_name': 'Discovery Log',
                'verbose_name_plural': 'Discovery Logs',
                'ordering': ['-started_at'],
            },
        ),
        migrations.AddField(
            model_name='gcpproject',
            name='organization',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='projects', to='gcp.gcporganization'),
        ),
        migrations.AddField(
            model_name='gcpproject',
            name='discovered',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='gcpproject',
            name='last_synced',
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='computeinstance',
            name='discovered',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='computeinstance',
            name='last_synced',
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='computeinstance',
            name='self_link',
            field=models.URLField(blank=True, max_length=500),
        ),
        migrations.AddField(
            model_name='vpcnetwork',
            name='discovered',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='vpcnetwork',
            name='last_synced',
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='vpcnetwork',
            name='self_link',
            field=models.URLField(blank=True, max_length=500),
        ),
        migrations.AddField(
            model_name='subnet',
            name='discovered',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='subnet',
            name='last_synced',
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='subnet',
            name='self_link',
            field=models.URLField(blank=True, max_length=500),
        ),
        migrations.AddField(
            model_name='firewallrule',
            name='discovered',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='firewallrule',
            name='last_synced',
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='firewallrule',
            name='self_link',
            field=models.URLField(blank=True, max_length=500),
        ),
        migrations.AddField(
            model_name='cloudrouter',
            name='discovered',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='cloudrouter',
            name='last_synced',
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='cloudrouter',
            name='self_link',
            field=models.URLField(blank=True, max_length=500),
        ),
        migrations.AddField(
            model_name='cloudsqlinstance',
            name='discovered',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='cloudsqlinstance',
            name='last_synced',
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='cloudsqlinstance',
            name='self_link',
            field=models.URLField(blank=True, max_length=500),
        ),
        migrations.AddField(
            model_name='cloudstoragebucket',
            name='discovered',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='cloudstoragebucket',
            name='last_synced',
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='cloudstoragebucket',
            name='self_link',
            field=models.URLField(blank=True, max_length=500),
        ),
        migrations.AddField(
            model_name='gkecluster',
            name='discovered',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='gkecluster',
            name='last_synced',
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='gkecluster',
            name='self_link',
            field=models.URLField(blank=True, max_length=500),
        ),
        migrations.AddField(
            model_name='serviceaccount',
            name='discovered',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='serviceaccount',
            name='last_synced',
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='vpngateway',
            name='discovered',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='vpngateway',
            name='last_synced',
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='vpngateway',
            name='self_link',
            field=models.URLField(blank=True, max_length=500),
        ),
        migrations.AddField(
            model_name='vpntunnel',
            name='discovered',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='vpntunnel',
            name='last_synced',
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='vpntunnel',
            name='self_link',
            field=models.URLField(blank=True, max_length=500),
        ),
    ]
