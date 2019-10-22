from datetime import date
import os
import re
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from .models import Article, Author, Author_Article, Journal
from add_article import search, get_detail
from famine.search_pubmed import replace_tags

@login_required
@csrf_exempt
def add_journal(request):
    if request.method == 'GET':
        journals = Journal.objects.all()
        return render(request, "Article/add_journal.html", {'journals': journals})

    if request.method == "POST":
        name = request.POST.get('name')
        ifactor = request.POST.get('ifactor')

        try:
            ifactor = float(ifactor)
        except ValueError:
            return HttpResponse('3')

        jour = Journal.objects.filter(name=name)
        if jour:
            return HttpResponse('2')
        else:
            Journal.objects.create(name=name, ifactor=ifactor)
            return HttpResponse('1')


@login_required
@csrf_exempt
@require_POST
def edit_journal(request):
    jour_id = request.POST.get('id')
    name = request.POST.get('name')
    ifactor = request.POST.get('ifactor')

    try:
        ifactor = float(ifactor)
    except ValueError:
        return HttpResponse('3')

    try:
        journal = Journal.objects.get(id=jour_id)
        journal.name = name
        journal.ifactor = ifactor
        journal.save()
        return HttpResponse('1')
    except:
        return HttpResponse('0')


@login_required
@csrf_exempt
@require_POST
def del_journal(request):
    jour_id = request.POST.get("id")
    try:
        journal = Journal.objects.get(id=jour_id)
        journal.delete()
        return HttpResponse("1")
    except:
        return HttpResponse("2")

@login_required
@csrf_exempt
def add_article(request):
    if request.method == 'GET':
        today = date.today().strftime("%Y/%m/%d")
        journals = Journal.objects.all()
        defaut_dict = {'fdate': "", 'tdate': today}
        return render(request, "Article/add_paper.html", {'journals': journals, 'dict': defaut_dict})

    if request.method == 'POST':
        jour = request.POST.get('journal')
        fdate = request.POST.get('fdate')
        tdate = request.POST.get('tdate')
        if not jour:
            return HttpResponse('-4')
        if fdate:
            fdate = fdate.replace('-', '/')
        if tdate:
            tdate = tdate.replace('-', '/')
        if not re.match(r'\d{4}/\d{2}/\d{2}', fdate) or not re.match(r'\d{4}/\d{2}/\d{2}', tdate):
            return HttpResponse('-3')
        journal = Journal.objects.get(id=jour)
        try:
            records, az = search(journal.name, fdate, tdate)
        except:
            return HttpResponse('-6')
        if records:
            try:
                authors_list, article_list = get_detail(replace_tags(az))
            except:
                return HttpResponse('-5')
        else:
            return HttpResponse('-2')

        try:
            count = 0
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
                count += 1
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
            return HttpResponse(str(count))
        except:
            return HttpResponse('-1')
