# Generated by Django 4.2.5 on 2023-11-02 03:02

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('lagu', '0043_alter_hoadoncoctien_ngay_thanh_toan_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='hoadoncoctien',
            name='ngay_thanh_toan',
            field=models.DateTimeField(default=datetime.datetime(2023, 11, 2, 10, 2, 9, 189599)),
        ),
    ]
