# Generated by Django 4.2.5 on 2023-11-27 10:46

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('lagu', '0070_list_actived_status'),
    ]

    operations = [
        migrations.AlterField(
            model_name='manage',
            name='name',
            field=models.CharField(max_length=255, unique=True),
        ),
    ]
