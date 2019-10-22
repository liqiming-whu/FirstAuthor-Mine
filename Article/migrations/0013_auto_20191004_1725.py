# Generated by Django 2.2.5 on 2019-10-04 09:25

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('Article', '0012_auto_20191002_1509'),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name='author',
            unique_together=None,
        ),
        migrations.RemoveField(
            model_name='firstauthor',
            name='article',
        ),
        migrations.RemoveField(
            model_name='firstauthor',
            name='author',
        ),
        migrations.AlterUniqueTogether(
            name='journal',
            unique_together=None,
        ),
        migrations.DeleteModel(
            name='Article',
        ),
        migrations.DeleteModel(
            name='Author',
        ),
        migrations.DeleteModel(
            name='FirstAuthor',
        ),
        migrations.DeleteModel(
            name='Journal',
        ),
    ]