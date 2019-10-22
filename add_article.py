import os
import re
from datetime import date
from entrezpy.efetch.efetcher import Efetcher
import xml.etree.ElementTree as ET
from entrezpy.efetch.efetch_analyzer import EfetchAnalyzer
from famine.search_pubmed import search_pubmed
from create_database import FirstAuthorArticle, get_topic, isChinese
from famine.search_pubmed import replace_tags

user_email = "yu.zhou@whu.edu.cn"


class PubmedAnalyzer(EfetchAnalyzer):
    def __init__(self):
        super().__init__()
        self.value = None

    def analyze_result(self, response, request):
        self.init_result(response, request)
        self.value = response.getvalue()

    def isEmpty(self):
        if self.value:
            return False
        return True

    def get_result(self):
        return self.value


def efetch_pubmed(idlist, email=user_email):
    e = Efetcher('Efetch', email)
    az = e.inquire({
        'db': 'pubmed',
        'id': idlist,
        'retmode': 'xml'}, PubmedAnalyzer()).get_result()
    return az


def search(journal, mindate, maxdate):
    if not maxdate:
        maxdate = date.today().strftime("%Y/%m/%d")
    az = None
    idlist = search_pubmed(journal, mindate, maxdate, email=user_email)
    count = len(idlist)
    if count > 0:
        az = efetch_pubmed(idlist)
    return count, az


def get_detail(xml_str):
    root = ET.fromstring(xml_str)
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
        if len(pubtype_set.intersection(
                set(['Journal Article', 'Letter']))) == 0:
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
            if affiliation:
                search_email = re.findall(r"\S+\@\S+", affiliation)
                email_number = len(set(search_email))
                if email_number > 1:
                    affiliation = affiliation.replace(" ".join(search_email), "")
                    au_email.append(name)
                    try:
                        email = search_email[au_email.index(name)]
                    except:
                        email = None
                elif email_number == 1:
                    email = search_email[0]
                    affiliation = affiliation.replace(email, "")
                    affiliation = affiliation.replace(" Electronic address:", "")
                else:
                    email = None
                if email is not None and email[-1] == '.':
                    email = email[:-1]
            else:
                affiliation = None
                email = None
            authors.append([name, first, last, chinese, affiliation, email])
        if Chinese_num > 0:
            article_list.append([p.pubmed_id[:8], p.publication_date,
                                 p.title, p.abstract, p.doi, topic])
            authors_list.append(authors)
    return authors_list, article_list
