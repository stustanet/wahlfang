# Generated by Django 3.1.2 on 2020-11-02 17:48

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ('vote', '0019_auto_20201030_1913'),
    ]

    operations = [
        migrations.AddField(
            model_name='election',
            name='remind_text_sent',
            field=models.BooleanField(default=False),
        ),
    ]
