# Generated by Django 5.0.6 on 2025-07-20 14:43

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0004_analyticsdata_user_agent'),
    ]

    operations = [
        migrations.AlterField(
            model_name='campaign',
            name='organization_approval_status',
            field=models.CharField(choices=[('Pending Organization Review', 'Pending Organization Review'), ('Approved by Organization', 'Approved by Organization'), ('Rejected by Organization', 'Rejected by Organization'), ('Active (Org)', 'Active (Organization Approved)'), ('N/A', 'N/A')], default='N/A', max_length=30),
        ),
    ]
