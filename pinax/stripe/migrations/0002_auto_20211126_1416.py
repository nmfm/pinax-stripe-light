# Generated by Django 3.2.9 on 2021-11-26 20:16

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('pinax_stripe', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='event',
            name='validated_message',
            field=models.JSONField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='event',
            name='webhook_message',
            field=models.JSONField(),
        ),
    ]
