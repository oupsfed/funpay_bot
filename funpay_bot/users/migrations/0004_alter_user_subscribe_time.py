# Generated by Django 3.2.18 on 2023-04-11 12:31

import datetime

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0003_alter_user_subscribe_time'),
    ]

    operations = [
        migrations.AlterField(
            model_name='user',
            name='subscribe_time',
            field=models.DateTimeField(default=datetime.datetime(2023, 4, 14, 15, 31, 23, 882245)),
        ),
    ]
