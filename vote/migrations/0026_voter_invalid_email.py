# Generated by Django 3.1.8 on 2021-05-01 16:51

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('vote', '0025_session_spectator_token'),
    ]

    operations = [
        migrations.AddField(
            model_name='voter',
            name='invalid_email',
            field=models.BooleanField(default=False),
        ),
    ]
