import os
import re
import xml.etree.ElementTree as ET
import django
from pymed.article import PubMedArticle
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'famine_site.settings')
django.setup()
from Article.models import Article, Author, Author_Article, Journal
from famine.search_pubmed import replace_tags
from add_article import search, get_detail


def start_search(name, fdate, tdate):
    journal = Journal.objects.get(name=name)
    count, az = search(name, fdate, tdate)
    if az:
        authors_list, article_list = get_detail(replace_tags(az))

    for authors, article in zip(authors_list, article_list):
        Article_obj = Article.objects.filter(pmid=article[0])
        if Article_obj:
            continue
        else:
            Article.objects.create(
                pmid=article[0],
                journal=journal,
                pubdate=article[1],
                title=article[2],
                abstract=article[3],
                doi=article[4],
                subject=article[5])

        Article_object = Article.objects.get(pmid=article[0])
        rank = 1
        for author in authors:
            Author_obj = Author.objects.filter(name=author[0], affiliation=author[4], email=author[5])
            if not Author_obj:
                Author.objects.create(
                    name=author[0],
                    first=author[1],
                    last=author[2],
                    chinese=author[3],
                    affiliation=author[4],
                    email=author[5])
            Author_object = Author.objects.get(name=author[0], affiliation=author[4], email=author[5])
            try:
                if rank == 1:
                    Author_Article.objects.create(author=Author_object, article=Article_object, rank=rank, first='Yes')
                else:
                    Author_Article.objects.create(author=Author_object, article=Article_object, rank=rank)
            except:
                continue
            rank += 1


if __name__ == '__main__':
    journals = ("Nature", "Science", "Cell")
    for journal in journals:
        start_search(journal, '2019/10/01', '2019/10/31')
