# Generated by Django 4.2.5 on 2023-10-20 16:25

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('lagu', '0038_hoadonthanhtoan_menus_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='hoadoncoctien',
            name='ngay_thanh_toan',
            field=models.DateTimeField(default=datetime.datetime(2023, 10, 20, 23, 25, 27, 865381)),
        ),
    ]
