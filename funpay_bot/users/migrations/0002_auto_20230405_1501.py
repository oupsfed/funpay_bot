# Generated by Django 3.2.18 on 2023-04-05 12:01

import datetime

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='user',
            name='subscribe_time',
            field=models.DateTimeField(default=datetime.datetime(2023, 4, 8, 15, 1, 25, 392939)),
        ),
        migrations.AlterField(
            model_name='user',
            name='telegram_chat_id',
            field=models.IntegerField(default=0),
        ),
    ]
