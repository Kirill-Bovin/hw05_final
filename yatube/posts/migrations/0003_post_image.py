# Generated by Django 2.2.19 on 2022-12-06 14:31

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('posts', '0002_auto_20221203_1832'),
    ]

    operations = [
        migrations.AddField(
            model_name='post',
            name='image',
            field=models.ImageField(blank=True, upload_to='posts/', verbose_name='Картинка'),
        ),
    ]
