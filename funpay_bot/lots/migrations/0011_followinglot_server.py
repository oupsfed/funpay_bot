# Generated by Django 3.2.18 on 2023-04-11 13:04

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('lots', '0010_alter_item_server'),
    ]

    operations = [
        migrations.AddField(
            model_name='followinglot',
            name='server',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='following', to='lots.server'),
        ),
    ]
