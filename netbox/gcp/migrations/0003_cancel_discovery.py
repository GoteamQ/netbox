from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ('gcp', '0002_organization_discovery'),
    ]

    operations = [
        migrations.AddField(
            model_name='gcporganization',
            name='cancel_requested',
            field=models.BooleanField(default=False, help_text='Cancel the current discovery run'),
        ),
        migrations.AlterField(
            model_name='gcporganization',
            name='discovery_status',
            field=models.CharField(
                choices=[
                    ('pending', 'Pending'),
                    ('running', 'Running'),
                    ('canceling', 'Canceling'),
                    ('canceled', 'Canceled'),
                    ('completed', 'Completed'),
                    ('failed', 'Failed'),
                ],
                default='pending',
                max_length=50,
            ),
        ),
        migrations.AlterField(
            model_name='discoverylog',
            name='status',
            field=models.CharField(
                choices=[
                    ('running', 'Running'),
                    ('canceled', 'Canceled'),
                    ('completed', 'Completed'),
                    ('failed', 'Failed'),
                ],
                default='running',
                max_length=50,
            ),
        ),
    ]
