# Generated by Django 3.2.13 on 2022-07-09 13:53

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('reservations', '0004_auto_20220703_0818'),
    ]

    operations = [
        migrations.AlterField(
            model_name='bookedday',
            name='reservation',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='bookeddays', to='reservations.reservation'),
        ),
    ]
