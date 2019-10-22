import os
import re
import xml.etree.ElementTree as ET
import django
from pymed.article import PubMedArticle
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'famine_site.settings')
django.setup()
from Article.models import Article, Author, Author_Article, Journal
from famine.topic import TopicPred
from famine.search_pubmed import replace_tags

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
FAMINE = os.path.join(BASE_DIR, 'famine')
FAMINE_DATA = os.path.join(FAMINE, 'data')
chineseLast = set(line.rstrip() for line in open(os.path.join(FAMINE, 'ChineseFamily.csv')))
chineseFirst = set(line.rstrip() for line in open(os.path.join(FAMINE, 'ChineseFirst.csv'))) 
journal_if = list(line.rstrip().split(',') for line in open(os.path.join(FAMINE, 'Journal_if.csv')))
tp = TopicPred(os.path.join(FAMINE_DATA, 'word_dict.pikle'), os.path.join(FAMINE_DATA, 'train_model.m'))


class FirstAuthorArticle(PubMedArticle):
    def get_pubtypes(self):
        path = ".//PublicationType"
        return [
            pubtype.text for pubtype in self.xml.findall(path) if pubtype is not None
        ]


def get_topic(journal, abstract):
    if 'cell' in journal or 'immunology' in journal:
        topic = "Biology"
    elif 'physics' in journal:
        topic = "Physics"
    elif 'chemistry' in journal:
        topic = "Chemistry"
    elif 'robotics' in journal:
        topic = "Computer science"
    else:
        topic = tp.classify(abstract)

    return topic


def isChinese(first, last):
    first = first.lower().replace("-", "")
    last = last.lower()
    if last in chineseLast and first in chineseFirst:
        return 'Yes'
    else:
        return 'No'


def fa_Chinese(f_pubmed):
    tree = ET.parse(f_pubmed)
    root = tree.getroot()
    article_list = list()
    authors_list = list()
    for article in root.iter("PubmedArticle"):
        p = FirstAuthorArticle(xml_element=article)

        if len(p.authors) == 0:
            continue

        if p.title.startswith("Author Correction:"):
            continue

        if len(p.title) == 0:
            continue
        p.title = replace_tags(p.title, reverse=True)

        pubtype_set = set(p.get_pubtypes())

        if len(pubtype_set.intersection(set(['Journal Article', 'Letter']))) == 0:
            continue

        if p.abstract is None:
            continue
        p.abstract = replace_tags(p.abstract, reverse=True)
        topic = get_topic(p.journal, p.abstract)
        authors = list()
        au_email = list()

        Chinese_num = 0
        flag = 0
        for author in p.authors:
            flag += 1
            first = author["firstname"]
            last = author["lastname"]
            if first is None or last is None:
                break
            name = first+" "+last
            chinese = isChinese(first, last)

            if chinese == 'Yes':
                Chinese_num += 1
            if flag == 3 and Chinese_num == 0:
                break
            affiliation = author["affiliation"]
            search_email = re.findall(r"\S+\@\S+", affiliation)
            if len(set(search_email)) > 1:
                affiliation = affiliation.replace(" ".join(search_email), "")

                au_email.append(name)
                email = search_email[au_email.index(name)]
            elif len(set(search_email)) == 1:
                email = search_email[0]
                affiliation = affiliation.replace(email, "")
                affiliation = affiliation.replace(" Electronic address:", "")
            else:
                email = None
            if email is not None and email[-1] == '.':
                email = email[:-1]

            print(name+'\n'+str(email)+'\n'+affiliation+'\n')

            authors.append([name, first, last, chinese, affiliation, email])

        if Chinese_num > 0:
            article_list.append([p.pubmed_id[:8], p.publication_date,
                                 p.title, p.abstract, p.doi, topic])
            authors_list.append(authors)

    return authors_list, article_list


if __name__ == '__main__':
    for jour_if in journal_if:
        print(jour_if[0], journal_if[1])
        Journal.objects.get_or_create(name=jour_if[0], ifactor=jour_if[1])

    journals = ("Nature", "Science", "Cell")
    for journal in journals:
        print("\n\n=======%s======\n\n" % journal)
        f_pubmed = os.path.join("famine/pub", "%s.xml" % journal)
        authors_list, article_list = fa_Chinese(f_pubmed)
        journal_object = Journal.objects.get(name=journal)

        for authors, article in zip(authors_list, article_list):

            Article_obj = Article.objects.filter(pmid=article[0])
            if Article_obj:
                continue
            else:
                Article.objects.create(
                    pmid=article[0],
                    journal=journal_object,
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
