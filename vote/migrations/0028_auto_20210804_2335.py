# Generated by Django 3.1.13 on 2021-08-04 21:35

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('vote', '0027_change_field_type_results_published'),
    ]

    operations = [
        migrations.AlterField(
            model_name='application',
            name='election',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='applications', to='vote.election'),
        ),
        migrations.AlterField(
            model_name='application',
            name='voter',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='applications', to='vote.voter'),
        ),
    ]
