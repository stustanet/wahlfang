# Generated by Django 3.0.5 on 2020-05-29 20:50

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('vote', '0003_auto_20200529_2118'),
    ]

    operations = [
        migrations.AlterField(
            model_name='election',
            name='session',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='elections', to='vote.Session'),
        ),
    ]
