# Generated by Django 3.2.6 on 2021-09-04 09:24

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('reciperecommend', '0013_auto_20210904_1024'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='dishhistory',
            name='cover_amt',
        ),
        migrations.AddField(
            model_name='dishhistory',
            name='carbohydrate',
            field=models.FloatField(default=0, verbose_name='炭水化物'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='dishhistory',
            name='recommend_dish',
            field=models.TextField(blank=True, null=True, verbose_name='おすすめの組み合わせ'),
        ),
    ]