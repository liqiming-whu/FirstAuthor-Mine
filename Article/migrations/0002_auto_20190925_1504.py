# Generated by Django 2.2.5 on 2019-09-25 07:04

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('Article', '0001_initial'),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name='author',
            unique_together=None,
        ),
        migrations.DeleteModel(
            name='Article',
        ),
        migrations.DeleteModel(
            name='Author',
        ),
    ]