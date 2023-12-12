# Generated by Django 4.2.5 on 2023-11-02 03:05

import datetime
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('lagu', '0044_alter_hoadoncoctien_ngay_thanh_toan'),
    ]

    operations = [
        migrations.AlterField(
            model_name='hoadoncoctien',
            name='ds_dat_ban',
            field=models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to='lagu.dsdatban'),
        ),
        migrations.AlterField(
            model_name='hoadoncoctien',
            name='ngay_thanh_toan',
            field=models.DateTimeField(default=datetime.datetime(2023, 11, 2, 10, 5, 58, 439544)),
        ),
    ]