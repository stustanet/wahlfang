# Generated by Django 3.0.5 on 2020-04-22 22:41

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('vote', '0004_auto_20200423_0025'),
    ]

    operations = [
        migrations.AlterField(
            model_name='vote',
            name='vote',
            field=models.CharField(choices=[('accept', 'für'), ('reject', 'gegen'), ('abstention', 'Enthaltung')], max_length=10),
        ),
    ]