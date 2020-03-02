# Generated by Django 2.2.3 on 2019-12-05 15:50

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('adv', '0002_tmptbl'),
    ]

    operations = [
        migrations.CreateModel(
            name='Area',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('AreaName', models.CharField(max_length=45)),
            ],
        ),
        migrations.CreateModel(
            name='City',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('CityName', models.CharField(max_length=45)),
            ],
        ),
        migrations.CreateModel(
            name='Country',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('CountryName', models.CharField(max_length=45)),
            ],
        ),
        migrations.CreateModel(
            name='State',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('StateName', models.CharField(max_length=45)),
                ('CountryId', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='adv.Country')),
            ],
        ),
        migrations.DeleteModel(
            name='TmpTbl',
        ),
        migrations.AddField(
            model_name='city',
            name='StateId',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='adv.State'),
        ),
        migrations.AddField(
            model_name='area',
            name='CityId',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='adv.City'),
        ),
    ]
