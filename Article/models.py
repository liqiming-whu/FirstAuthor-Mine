from django.db import models


class Author(models.Model):
    name = models.CharField(max_length=50, db_index=True)
    first = models.CharField(max_length=20)
    last = models.CharField(max_length=20)
    chinese = models.CharField(max_length=3, db_index=True)
    affiliation = models.TextField(null=True)
    email = models.EmailField(null=True)

    def __str__(self):
        return self.name

    class Meta:
        unique_together = ('name', 'affiliation', 'email')


class Journal(models.Model):
    name = models.CharField(max_length=50, db_index=True)
    ifactor = models.FloatField()

    def __str__(self):
        return self.name

    class Meta:
        unique_together = ('name', 'ifactor')


class Article(models.Model):
    pmid = models.CharField(max_length=8, primary_key=True)
    journal = models.ForeignKey(to='Journal', on_delete=models.CASCADE)
    pubdate = models.DateField(db_index=True)
    title = models.CharField(max_length=200)
    authors = models.ManyToManyField(to='Author', through='Author_Article', through_fields=('article', 'author'))
    abstract = models.TextField()
    doi = models.CharField(max_length=30)
    subject = models.CharField(max_length=20, db_index=True)

    def __str__(self):
        return self.pmid

    class Meta:
        ordering = ('-pubdate',)


class Author_Article(models.Model):
    author = models.ForeignKey(to='Author', on_delete=models.CASCADE)
    article = models.ForeignKey(to='Article', on_delete=models.CASCADE)
    rank = models.IntegerField()
    first = models.CharField(max_length=3, null=True, db_index=True)
    cofirst = models.CharField(max_length=3, null=True, db_index=True)

    def __str__(self):
        return self.author.name

    class Meta:
        unique_together = ('author', 'article')
