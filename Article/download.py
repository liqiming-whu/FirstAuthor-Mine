import re
import xlwt
from io import BytesIO
from django.db.models import Q
from .models import Author_Article, Journal


def get_subject(topic):
    if topic == '1':
        return 'Biology'
    if topic == '2':
        return 'Physics'
    if topic == '3':
        return 'Chemistry'
    if topic == '4':
        return 'Computer science'
    if topic == '5':
        return 'Other'

def search_query(request):
    journals = Journal.objects.all()
    First_authors = Author_Article.objects.filter(Q(first='Yes') | Q(cofirst='Yes'), author__chinese='Yes')

    if request.method == 'GET':
        name = request.GET.get('name', '')
        rela = request.GET.get('rela', '1')
        journal = request.GET.get('journal')
        reand = request.GET.get('reand', '1')
        topic = request.GET.get('topic')
        andor = request.GET.get('andor', '1')
        fdate = request.GET.get('fdate', 'yyyy-mm-dd')
        tdate = request.GET.get('tdate', 'yyyy-mm-dd')
        order = request.GET.get('order', '1')
        page = request.GET.get('page')

        if name:
            name = name.replace("_", " ")
        default_dict = {'name': name, 'fdate': fdate,
                        'tdate': tdate, 'rela': rela,
                        'journal': journal, 'reand': reand,
                        'topic': topic, 'andor': andor,
                        'order':order}
        if not topic or topic == 'None':
            topic = 0
        if journal:
            journal = journal.split(',')
        if journal == ['None']:
            journal = None
        js_dict = {'rela': int(rela)-1, 'journal': journal,
                   'reand': int(reand)-1, 'topic': int(topic),
                   'andor': int(andor)-1, 'order': int(order)-1}

    if request.method == 'POST':
        name = request.POST.get('name')
        rela = request.POST.get('rela')
        journal = request.POST.getlist('journal')
        reand = request.POST.get('reand')
        topic = request.POST.get('topic')
        andor = request.POST.get('andor')
        fdate = request.POST.get('fdate')
        tdate = request.POST.get('tdate')
        order = request.POST.get('order')
        page = 1
        journal_str = ""
        for i in journal:
            journal_str = journal_str + i + ','
        if journal == ['None']:
            journal = None
        if not topic:
            topic = 0
        if name:
            name = name.replace("_", " ")
        default_dict = {'name': name, 'fdate': fdate,
                        'tdate': tdate, 'rela': rela,
                        'journal': journal_str[:-1],
                        'reand': reand, 'topic': topic,
                        'andor': andor, 'order': order}
        js_dict = {'rela': int(rela)-1, 'journal': journal,
                   'reand': int(reand)-1, 'topic': int(topic),
                   'andor': int(andor)-1, 'order': int(order)-1}
    con = Q()
    datecon = Q()
    if name:
        q1 = Q(author__name__icontains=name)
        con.add(q1, 'OR')

    journal_lst = ''
    if journal:
        q2 = Q()
        q2.connector = ('OR')
        for jour in journal:
            j = Journal.objects.get(id=jour)
            journal_lst = journal_lst + j.name + ", "
            q2.children.append(('article__journal', j))
        if rela == '1':
            con.add(q2, 'AND')
        else:
            con.add(q2, 'OR')

    if int(topic):
        subject = get_subject(topic)
        q3 = Q(article__subject=subject)
        if andor == '1':
            con.add(q3, 'AND')
        else:
            con.add(q3, 'OR') 


    if re.match(r'\d{4}-\d{2}-\d{2}', fdate):
        q3 = Q(article__pubdate__gte=fdate)
        datecon.add(q3, 'OR')
    else:
        fdate = None

    if re.match(r'\d{4}-\d{2}-\d{2}', tdate):
        q4 = Q(article__pubdate__lte=tdate)
        datecon.add(q4, 'AND')
    else:
        tdate = None

    if reand == '1':
        First_authors = First_authors.filter(con, datecon)
    else:
        First_authors = First_authors.filter(con | datecon)

    return First_authors, journals, default_dict, js_dict, journal_lst, page, order


def download_article(First_authors):
    workbook = xlwt.Workbook(encoding='utf-8')
    worksheet = workbook.add_sheet('sheet1')

    title = ('Name', 'Journal', 'Date', 'First', 'Co-first', 'Rank', 'Topic', 'Title', 'Affiliation')
    for col, key in enumerate(title):
        worksheet.write(0, col, key)

    for row, article in enumerate(First_authors):
        content = (article.author.name, article.article.journal.name,
                   article.article.pubdate.strftime('%Y-%m-%d'), article.first,
                   article.cofirst, article.rank,
                   article.article.subject, article.article.title,
                   article.author.affiliation)
        for col, key in enumerate(content):
            worksheet.write(row+1, col, key)

    output = BytesIO()
    workbook.save(output)
    output.seek(0)

    return output


def download_author(authors_info):
    workbook = xlwt.Workbook(encoding='utf-8')
    worksheet = workbook.add_sheet('sheet1')

    title = ('Name', 'Affiliation', 'IFscore', 'Paper', 'Email')

    for col, key in enumerate(title):
        worksheet.write(0, col, key)

    for row, author in enumerate(authors_info):
        worksheet.write(row+1, 0, author[0].name)
        worksheet.write(row+1, 1, author[0].affiliation)
        worksheet.write(row+1, 2, author[1])
        paper = ''
        for au in author[2]:
            if au.first and not au.cofirst:
                paper = paper + au.article.journal.name + ' ' + au.article.pubdate.strftime('%Y-%m-%d') + ' ' + 'first author; '
            if au.first and au.cofirst:
                paper = paper + au.article.journal.name + ' ' + au.article.pubdate.strftime('%Y-%m-%d') + ' ' + 'cofirst author 1; '
            if not au.first and au.cofirst:
                paper = paper + au.article.journal.name + ' ' + au.article.pubdate.strftime('%Y-%m-%d') + ' ' + 'cofirst author ' + str(au.rank) + '; '
        worksheet.write(row+1, 3, paper)
        worksheet.write(row+1, 4, author[0].email)

    output = BytesIO()
    workbook.save(output)
    output.seek(0)

    return output
