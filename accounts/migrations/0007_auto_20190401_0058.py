# Generated by Django 2.1.7 on 2019-04-01 00:58

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0006_auto_20190401_0055'),
    ]

    operations = [
        migrations.RenameField(
            model_name='usersocialnetwork',
            old_name='birthdate',
            new_name='birthday',
        ),
        migrations.RemoveField(
            model_name='profile',
            name='birthdate',
        ),
        migrations.AddField(
            model_name='profile',
            name='birthday',
            field=models.DateField(blank=True, null=True, verbose_name='Birthday'),
        ),
    ]
