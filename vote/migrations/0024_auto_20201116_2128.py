# Generated by Django 3.1.2 on 2020-11-16 20:28

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ('vote', '0023_election_disable_abstention'),
    ]

    operations = [
        migrations.AlterField(
            model_name='election',
            name='result_published',
            field=models.CharField(choices=[('0', 'unpublished'), ('1', 'published')], default='0', max_length=1),
        ),
    ]