# Generated by Django 3.0.6 on 2020-05-30 16:36

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('vote', '0005_auto_20200530_0019'),
    ]

    operations = [
        migrations.AlterField(
            model_name='election',
            name='max_votes_yes',
            field=models.IntegerField(blank=True, null=True),
        ),
    ]
