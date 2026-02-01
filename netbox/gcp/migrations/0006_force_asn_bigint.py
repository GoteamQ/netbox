from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ('gcp', '0005_fix_asn_field_size'),
    ]

    operations = [
        migrations.RunSQL(
            'ALTER TABLE gcp_cloudrouter ALTER COLUMN asn TYPE bigint;',
            reverse_sql='ALTER TABLE gcp_cloudrouter ALTER COLUMN asn TYPE integer;',
        ),
    ]
