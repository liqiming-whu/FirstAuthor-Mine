#!/usr/bin/env python3
"""
Parse articles in XML from PubMed
"""
import os
import xml.etree.ElementTree as ET
from pymed.article import PubMedArticle
import xlsxwriter
from topic import TopicPred

chineseLast = set(line.rstrip() for line in open("ChineseFamily.csv"))
chineseFirst = set(line.rstrip() for line in open("ChineseFirst.csv"))
tp = TopicPred("data/word_dict.pikle", "data/train_model.m")


class FirstAuthorArticle(PubMedArticle):
    def get_pubtypes(self):
        path = ".//PublicationType"
        return [
            pubtype.text for pubtype in self.xml.findall(path) if pubtype is not None
        ]


def fa_chinese(f_pubmed, worksheet):
    tree = ET.parse(f_pubmed)
    root = tree.getroot()
    row = 0
    col = 0
    worksheet.write_row(row, col, tuple([
        "PubMedID", "Journal", "Topic", "PubDate", "FirstAuthor", "Affiliation", "Title"
    ]))
    row += 1
    for article in root.iter("PubmedArticle"):
        p = FirstAuthorArticle(xml_element=article)

        if len(p.authors) == 0:
            continue

        if p.title.startswith("Author Correction:"):
            continue

        pubtype_set = set(p.get_pubtypes())
        if len(pubtype_set.intersection(set(['Journal Article', 'Letter']))) == 0:
            continue

        fa = p.authors[0]
        if fa["firstname"] is None or fa["lastname"] is None:
            continue
        if fa["affiliation"] is None:
            continue

        first = fa["firstname"].lower().replace("-", "")
        last = fa["lastname"].lower()
        if last in chineseLast and first in chineseFirst:
            print(p.pubmed_id, pubtype_set, p.keywords)

            if p.journal == "Cell":
                topic = "Biology"
            else:
                topic = tp.classify(p.abstract)

            worksheet.write_row(row, col, tuple([
                p.pubmed_id, p.journal, topic, p.publication_date,
                "%s %s" % (first.capitalize(), last.capitalize()),
                fa["affiliation"], p.title
            ]))
            row += 1


workbook = xlsxwriter.Workbook('FirstAuthors.xlsx', {
    'default_date_format': 'yy/mm/dd'})

journals = ("Nature", "Science", "Cell")
for journal in journals:
    print("\n\n=======%s======\n\n" % journal)
    worksheet = workbook.add_worksheet(journal)
    f_pubmed = os.path.join("pub", "%s.xml" % journal)
    fa_chinese(f_pubmed, worksheet)

workbook.close()
