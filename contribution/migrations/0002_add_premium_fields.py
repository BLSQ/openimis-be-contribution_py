# Generated by Django 3.2.18 on 2023-05-12 12:15

import core.datetimes.ad_datetime
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('contribution', '0001_initial'),
        ('payer', '0001_initial'),
        ('policy', '0003_auto_20201021_0811'),
    ]

    operations = [
        migrations.AddField(
            model_name='premium',
            name='created_date',
            field=models.DateTimeField(db_column='CreatedDate', default=core.datetimes.ad_datetime.AdDatetime.now),
        ),
        migrations.AddField(
            model_name='premium',
            name='payer',
            field=models.ForeignKey(blank=True, db_column='PayerID', null=True, on_delete=django.db.models.deletion.DO_NOTHING, related_name='premiums', to='payer.payer'),
        ),
        migrations.AddField(
            model_name='premium',
            name='policy',
            field=models.ForeignKey(db_column='PolicyID', on_delete=django.db.models.deletion.DO_NOTHING, related_name='premiums', to='policy.policy'),
        ),
        migrations.AlterField(
            model_name='premium',
            name='is_offline',
            field=models.BooleanField(blank=True, db_column='isOffline', default=False, null=True),
        ),
        migrations.AlterField(
            model_name='premium',
            name='is_photo_fee',
            field=models.BooleanField(blank=True, db_column='isPhotoFee', default=False, null=True),
        ),
        migrations.AlterField(
            model_name='premium',
            name='pay_type',
            field=models.CharField(db_column='PayType', max_length=1),
        ),
    ]
