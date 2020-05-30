# Generated by Django 3.0.6 on 2020-05-29 22:19

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('vote', '0004_auto_20200529_2250'),
    ]

    operations = [
        migrations.AlterField(
            model_name='openvote',
            name='voter',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='open_votes', to='vote.Voter'),
        ),
    ]