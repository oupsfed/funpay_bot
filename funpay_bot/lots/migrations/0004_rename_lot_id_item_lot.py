# Generated by Django 3.2.18 on 2023-04-05 08:48

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('lots', '0003_item'),
    ]

    operations = [
        migrations.RenameField(
            model_name='item',
            old_name='lot_id',
            new_name='lot',
        ),
    ]
