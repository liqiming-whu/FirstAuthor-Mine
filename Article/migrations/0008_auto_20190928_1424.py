# Generated by Django 2.2.5 on 2019-09-28 06:24

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('Article', '0007_auto_20190928_1419'),
    ]

    operations = [
        migrations.CreateModel(
            name='Article',
            fields=[
                ('pmid', models.CharField(max_length=8, primary_key=True, serialize=False)),
                ('journal', models.CharField(max_length=20)),
                ('pubdate', models.DateField()),
                ('title', models.CharField(max_length=200)),
                ('abstract', models.TextField()),
                ('doi', models.CharField(max_length=30)),
                ('subject', models.CharField(max_length=20)),
            ],
        ),
        migrations.CreateModel(
            name='Author',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=50)),
                ('first', models.CharField(max_length=20)),
                ('last', models.CharField(max_length=20)),
                ('affiliation', models.TextField()),
                ('email', models.EmailField(max_length=254, null=True)),
            ],
            options={
                'unique_together': {('name', 'affiliation', 'email')},
            },
        ),
        migrations.CreateModel(
            name='FirstAuthor',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('rank', models.IntegerField()),
                ('fst', models.CharField(max_length=3, null=True)),
                ('co', models.CharField(max_length=3, null=True)),
                ('article', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='Article.Article')),
                ('author', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='Article.Author')),
            ],
        ),
        migrations.AddField(
            model_name='article',
            name='authors',
            field=models.ManyToManyField(through='Article.FirstAuthor', to='Article.Author'),
        ),
    ]
