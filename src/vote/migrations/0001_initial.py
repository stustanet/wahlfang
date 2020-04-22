# Generated by Django 3.0.5 on 2020-04-22 19:33

from django.db import migrations, models
import django.db.models.deletion
import uuid


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Candidate',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('last_name', models.CharField(max_length=256)),
                ('first_name', models.CharField(max_length=256)),
                ('application', models.TextField()),
                ('avatar', models.ImageField(null=True, upload_to='avatars/%Y/%m/%d')),
                ('email', models.EmailField(max_length=254)),
            ],
        ),
        migrations.CreateModel(
            name='Election',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=512)),
                ('start_date', models.DateTimeField()),
                ('end_date', models.DateTimeField()),
            ],
        ),
        migrations.CreateModel(
            name='Vote',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('vote', models.CharField(choices=[('accept', 'accept'), ('abstention', 'abstention'), ('reject', 'reject')], max_length=10)),
                ('candidate', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='votes', to='vote.Candidate')),
                ('election', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='votes', to='vote.Election')),
            ],
        ),
        migrations.CreateModel(
            name='Token',
            fields=[
                ('uuid', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('used', models.BooleanField(default=False)),
                ('email', models.EmailField(max_length=254)),
                ('election', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='tokens', to='vote.Election')),
            ],
        ),
        migrations.AddField(
            model_name='candidate',
            name='election',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='candidates', to='vote.Election'),
        ),
    ]
