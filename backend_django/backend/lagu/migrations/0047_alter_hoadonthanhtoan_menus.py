# Generated by Django 4.2.5 on 2023-11-02 03:14

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('lagu', '0046_alter_hoadoncoctien_ngay_thanh_toan'),
    ]

    operations = [
        migrations.AlterField(
            model_name='hoadonthanhtoan',
            name='menus',
            field=models.ManyToManyField(related_name='ds_mon_an', through='lagu.ChiTietHoaDon', to='lagu.menu'),
        ),
    ]