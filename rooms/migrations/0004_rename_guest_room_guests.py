# Generated by Django 3.2.13 on 2022-04-19 10:37

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('rooms', '0003_auto_20220418_1450'),
    ]

    operations = [
        migrations.RenameField(
            model_name='room',
            old_name='guest',
            new_name='guests',
        ),
    ]
