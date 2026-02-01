from django.db import migrations, models

class Migration(migrations.Migration):

    dependencies = [
        ('gcp', '0004_alter_clouddnsrecord_options_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='cloudrouter',
            name='asn',
            field=models.BigIntegerField(default=64512),
        ),
    ]
