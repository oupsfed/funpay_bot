# Generated by Django 3.2.18 on 2023-04-04 17:45

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('lots', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='game',
            name='loc',
            field=models.CharField(blank=True, max_length=50, null=True),
        ),
    ]
