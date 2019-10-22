#!/usr/bin/env python3
"""
Fetch First Authors from CNS papers
"""
import sys
from datetime import date
from entrezpy.esearch.esearcher import Esearcher
from entrezpy.efetch.efetcher import Efetcher
from entrezpy.efetch.efetch_analyzer import EfetchAnalyzer

JOURNALS = [
    ("Cell", "Biology"),
    ("Nature", None),
    ("Science", None),
]

user_email = "yu.zhou@whu.edu.cn"


class PubmedAnalyzer(EfetchAnalyzer):
    """Derive a simple but specialized analyzer from the default EfetchAnalyzer."""

    def __init__(self, fname):
        """Init a GenomeAssenbler with NCBI summary data. In case we need to fetch
        multiple requests, e.g. WGS shotgun sequences, set a file handler as
        attribute."""
        super().__init__()
        self.fname = fname
        self.fh = None

    def analyze_result(self, response, request):
        """Set file handler and filename if it's the first query request. Otherwise
        append. """
        self.init_result(response, request)
        self.fh = open(self.fname, 'w', encoding='utf-8')
        result = replace_tags(response.getvalue())
        self.fh.write(result)
        self.fh.close()

    def isEmpty(self):
        """Since the analyzer is not using a entrezpy.base.result.EutilsResult to
        store results, we have to overwrite the method to report empty results."""
        if self.fh:
            return False
        return True


def replace_tags(text, reverse=False):
    tags = ['<sup>', '</sup>', '<sub>', '</sub>', '<i>', '</i>']
    re_tags = ['[^', '^]', '[_', '_]', '[/', '/]']
    for tag, re_tag in zip(tags, re_tags):
        if reverse:
            text = text.replace(re_tag, tag)
        else:
            text = text.replace(tag, re_tag)

    return text


def search_pubmed(journal, mindate, maxdate, email=user_email):
    e = Esearcher('Esearch', email)
    res = e.inquire({
        'db': 'pubmed',
        'term': '%s[ta]' % journal,
        'sort': 'Date Released',
        'mindate': mindate,
        'maxdate': maxdate,
        'datetype': 'pdat',
        'retmax': 100000}).result
    return res.uids


def efetch_pubmed(idlist, outfile, email=user_email):
    e = Efetcher('Efetch', email)
    az = e.inquire({
        'db': 'pubmed',
        'id': idlist,
        'retmode': 'xml'}, PubmedAnalyzer(outfile)).get_result()
    return az


def search(journal, mindate, outfile):
    maxdate = date.today().strftime("%Y/%m/%d")
    sys.stderr.write("maxdate: %s\n" % maxdate)
    idlist = search_pubmed(journal, mindate, maxdate)
    sys.stderr.write("\nFetching %d articles ......\n\n" % len(idlist))
    if len(idlist) > 0:
        efetch_pubmed(idlist, outfile)


if __name__ == '__main__':
    if len(sys.argv) < 3:
        sys.stderr.write("Usage: program Nature 2019/05/01\n")
        sys.exit(1)
    journal, mindate = sys.argv[1:3]
    outfile = 'pub/%s.xml' % journal
    search(journal, mindate, outfile)
