# Generated by Django 3.2.6 on 2021-08-14 02:42

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='DishHistoryNutorition',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('name', models.CharField(max_length=50, verbose_name='料理名')),
                ('energy', models.IntegerField(verbose_name='エネルギー')),
                ('protein', models.FloatField(verbose_name='タンパク質')),
                ('fat', models.FloatField(verbose_name='脂質')),
                ('calcium', models.IntegerField(verbose_name='カルシウム')),
                ('iron', models.FloatField(verbose_name='鉄分')),
                ('vitamin_a', models.IntegerField(verbose_name='ビタミンA')),
                ('vitamin_b1', models.FloatField(verbose_name='ビタミンB1')),
                ('vitamin_b2', models.FloatField(verbose_name='ビタミンB2')),
                ('vitamin_c', models.IntegerField(verbose_name='ビタミンC')),
                ('result', models.IntegerField(blank=True, null=True)),
                ('proba', models.FloatField(default=0.0)),
                ('registered_date', models.DateField(default=datetime.date(2021, 8, 14))),
            ],
        ),
    ]
