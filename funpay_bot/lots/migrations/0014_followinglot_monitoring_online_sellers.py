# Generated by Django 3.2.18 on 2023-04-12 11:08

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('lots', '0013_followinglot_price'),
    ]

    operations = [
        migrations.AddField(
            model_name='followinglot',
            name='monitoring_online_sellers',
            field=models.BooleanField(default=False),
        ),
    ]
