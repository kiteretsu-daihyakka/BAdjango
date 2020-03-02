# Generated by Django 2.2.3 on 2019-12-08 14:06

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('adv', '0005_publisher'),
    ]

    operations = [
        migrations.CreateModel(
            name='Sahil',
            fields=[
                ('id', models.IntegerField(primary_key=True, serialize=False)),
                ('height', models.CharField(max_length=11)),
                ('width', models.CharField(max_length=11)),
            ],
            options={
                'db_table': 'sahil',
                'managed': False,
            },
        ),
        migrations.CreateModel(
            name='Temporarytbl',
            fields=[
                ('id', models.IntegerField(primary_key=True, serialize=False)),
                ('name', models.TextField()),
            ],
            options={
                'db_table': 'temporarytbl',
                'managed': False,
            },
        ),
    ]
