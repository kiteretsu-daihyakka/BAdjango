# Generated by Django 2.2.3 on 2019-12-07 08:49

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('adv', '0003_auto_20191205_2120'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='area',
            name='CityId',
        ),
        migrations.RemoveField(
            model_name='city',
            name='StateId',
        ),
        migrations.RemoveField(
            model_name='song',
            name='album',
        ),
        migrations.RemoveField(
            model_name='state',
            name='CountryId',
        ),
        migrations.DeleteModel(
            name='Album',
        ),
        migrations.DeleteModel(
            name='Area',
        ),
        migrations.DeleteModel(
            name='City',
        ),
        migrations.DeleteModel(
            name='Country',
        ),
        migrations.DeleteModel(
            name='Song',
        ),
        migrations.DeleteModel(
            name='State',
        ),
    ]
