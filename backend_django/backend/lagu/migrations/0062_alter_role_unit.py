# Generated by Django 4.2.5 on 2023-11-16 02:25

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('lagu', '0061_role'),
    ]

    operations = [
        migrations.AlterField(
            model_name='role',
            name='unit',
            field=models.CharField(max_length=100),
        ),
    ]
