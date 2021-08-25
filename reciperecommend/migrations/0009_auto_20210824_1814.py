# Generated by Django 3.2.6 on 2021-08-24 09:14

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('reciperecommend', '0008_auto_20210820_1002'),
    ]

    operations = [
        migrations.AlterField(
            model_name='dietaryreferenceintake',
            name='registered_date',
            field=models.DateField(default=datetime.date(2021, 8, 24)),
        ),
        migrations.AlterField(
            model_name='dishhistory',
            name='registered_date',
            field=models.DateField(default=datetime.date(2021, 8, 24)),
        ),
        migrations.AlterField(
            model_name='dishhistory',
            name='sim_dish_ip',
            field=models.TextField(blank=True, null=True, verbose_name='似ている料理:材料・工程'),
        ),
        migrations.AlterField(
            model_name='dishhistory',
            name='sim_dish_ntr',
            field=models.TextField(blank=True, null=True, verbose_name='似ている料理:栄養'),
        ),
        migrations.AlterField(
            model_name='dishmaster',
            name='registered_date',
            field=models.DateField(default=datetime.date(2021, 8, 24)),
        ),
    ]
