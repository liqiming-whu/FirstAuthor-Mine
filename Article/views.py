import json
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.db.models import Sum, Q
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from .models import Article, Author, Author_Article, Journal
from .download import search_query, download_article, download_author


@csrf_exempt
def First_author(request):
    if not request.user.is_authenticated:
        return HttpResponseRedirect('/famine/account/login')
    First_authors, journals, default_dict, js_dict, journal_lst, page, order = search_query(request)
    if order == '1':
        First_authors = First_authors.order_by('-article__pmid')
    else:
        First_authors = First_authors.order_by('article__pmid')

    if request.GET.get('download') == '1':
        output = download_article(First_authors)
        response = HttpResponse(content_type='application/vnd.ms-excel')
        response['Content-Disposition'] = 'attachment;filename=famine_result.xls'
        response.write(output.getvalue())

        return response

    paginator = Paginator(First_authors, 20, 10)
    try:
        First_authors_page = paginator.page(page)
    except PageNotAnInteger:
        First_authors_page = paginator.page(1)
    except EmptyPage:
        First_authors_page = paginator.page(paginator.num_pages)

    return render(request, "Article/first.html",
                  {"First_authors": First_authors_page,
                   "count": len(First_authors),
                   "journals": journals,
                   "dict": default_dict,
                   "js_dict": json.dumps(js_dict),
                   "journal_lst": journal_lst[:-2]})


@login_required
def Article_title(request):
    articles = Article.objects.all()
    paginator = Paginator(articles, 50, 20)
    page = request.GET.get('page')
    try:
        articles_page = paginator.page(page)
    except PageNotAnInteger:
        articles_page = paginator.page(1)
    except EmptyPage:
        articles_page = paginator.page(paginator.num_pages)
    return render(request, "Article/titles.html",
                  {"articles": articles_page, "count": len(articles)})


@login_required
def Article_detail(request, article_pmid):
    article = Article.objects.get(pmid=article_pmid)
    ranks = Author_Article.objects.filter(article=article_pmid)
    return render(request, "Article/content.html",
                  {"article": article, "ranks": ranks})

@csrf_exempt
@login_required
def Author_detail(request, author_id):
    author = Author.objects.get(id=author_id)
    articles = Author_Article.objects.filter(author=author_id)
    if request.method == 'GET':
        articles_for_score = articles.filter(Q(first='Yes') | Q(cofirst='Yes'))
        score = 0
        for article in articles_for_score:
            score += article.article.journal.ifactor

        return render(request, "Article/author.html",
                      {"author": author, "articles": articles, "score": score})

    if request.method == 'POST':
        email = request.POST.get('email')
        if email == 'None':
            email = None
        if email:
            same_author_obj = Author.objects.filter(~Q(id=author.id), name=author.name, email=email)
            if same_author_obj:
                same_author = same_author_obj[0]
                same_author_articles = Author_Article.objects.filter(author=same_author)
                same_author_article = same_author_articles[0]
                this_author_articles = Author_Article.objects.filter(author=author)
                this_author_article = this_author_articles[0]
                if same_author_article.article.pubdate > this_author_article.article.pubdate:
                    for article in this_author_articles:
                        article.author = same_author
                        article.save()
                    author.delete()
                    return HttpResponseRedirect('/famine/author/'+str(same_author.id))
                else:
                    for article in same_author_articles:
                        article.author = author
                        article.save()
                    same_author.delete()
                    return HttpResponseRedirect('/famine/author/'+str(author.id))
            else:
                author.email = email
                author.save()

        return HttpResponseRedirect('/famine/author/'+str(author.id))

@csrf_exempt
@require_POST
@login_required
def get_result(request, article_pmid):
    cofirst = request.POST.getlist('cofirst')
    chinese = request.POST.getlist('chinese')
    ranks = Author_Article.objects.filter(article=article_pmid)
    cofirst_ = list(str(author.author.id) for author in ranks)
    sub = list(i for i in cofirst_ if i not in cofirst)
    chinese_sub = list(i for i in cofirst_ if i not in chinese)
    author_1 = ranks.get(rank=1)

    for author_id in chinese:
        author = Author.objects.get(id=author_id)
        author.chinese = 'Yes'
        author.save()

    for author_id in chinese_sub:
        author = Author.objects.get(id=author_id)
        author.chinese = 'No'
        author.save()

    if len(cofirst) > 1:
        author_1.cofirst = 'Yes'
        author_1.save()
        for author_id in cofirst:
            author = ranks.get(author=author_id)
            if author.first == 'Yes':
                continue
            author.cofirst = 'Yes'
            author.save()
        for author_id in sub:
            author = ranks.get(author=author_id)
            if author.first == 'Yes':
                continue
            author.cofirst = None
            author.save()
    elif len(cofirst) == 1:
        author = ranks.get(author=cofirst[0])
        if author.first == 'Yes':
            author_1.cofirst = None
            author_1.save()
        else:
            author.cofirst = 'Yes'
            author.save()
            author_1.cofirst = 'Yes'
            author_1.save()
        for author_id in sub:
            author = ranks.get(author=author_id)
            if author.first == 'Yes':
                continue
            author.cofirst = None
            author.save()
    else:
        for author_id in sub:
            author = ranks.get(author=author_id)
            author.cofirst = None
            author.save()

    return HttpResponseRedirect('/famine/title/'+article_pmid)


@login_required
def journal(request, article_journal_name):
    journal = Journal.objects.get(name=article_journal_name)
    articles = Article.objects.filter(journal=journal)
    article_authors_list = list()
    for article in articles:
        first_author = Author_Article.objects.get(article=article, first='Yes')
        cofirst_author = Author_Article.objects.filter(article=article, cofirst='Yes')
        article_authors_list.append([article, first_author, cofirst_author])

    paginator = Paginator(article_authors_list, 20, 10)
    page = request.GET.get('page')
    try:
        article_authors_list_page = paginator.page(page)
    except PageNotAnInteger:
        article_authors_list_page = paginator.page(1)
    except EmptyPage:
        article_authors_list_page = paginator.page(paginator.num_pages)
    return render(request, "Article/journal.html",
                  {"article_authors_list": article_authors_list_page,
                   "journal": journal, "count": len(articles)}) 


@login_required
def topic(request, article_subject):
    articles = Article.objects.filter(subject=article_subject)
    article_authors_list = list()
    for article in articles:
        first_author = Author_Article.objects.get(article=article, first='Yes')
        cofirst_author = Author_Article.objects.filter(article=article, cofirst='Yes')
        article_authors_list.append([article, first_author, cofirst_author])

    paginator = Paginator(article_authors_list, 20, 10)
    page = request.GET.get('page')
    try:
        article_authors_list_page = paginator.page(page)
    except PageNotAnInteger:
        article_authors_list_page = paginator.page(1)
    except EmptyPage:
        article_authors_list_page = paginator.page(paginator.num_pages)

    return render(request, "Article/topic.html",
                  {"article_authors_list": article_authors_list_page,
                   "article_subject": article_subject,
                   "count": len(articles)})


@csrf_exempt
@login_required
def author(request):
    First_authors, journals, default_dict, js_dict, journal_lst, page, order = search_query(request)

    authors_info = list()
    if order == '1':
        authors_score = First_authors.values('author').annotate(score=Sum('article__journal__ifactor')).order_by('-score')
    else:
        authors_score = First_authors.values('author').annotate(score=Sum('article__journal__ifactor')).order_by('score')
    for au in authors_score:
        author = Author.objects.get(id=au['author'])
        score = round(au['score'], 2)
        articles = First_authors.filter(author=author)
        authors_info.append([author, score, articles])

    if request.GET.get('download') == '1':
        output = download_author(authors_info)
        response = HttpResponse(content_type='application/vnd.ms-excel')
        response['Content-Disposition'] = 'attachment;filename=famine_result.xls'
        response.write(output.getvalue())

        return response

    paginator = Paginator(authors_info, 20, 10)
    try:
        authors_info_page = paginator.page(page)
    except PageNotAnInteger:
        authors_info_page = paginator.page(1)
    except EmptyPage:
        authors_info_page = paginator.page(paginator.num_pages)

    return render(request, "Article/score.html",
                  {"authors_info": authors_info_page,
                   "journals": journals,
                   "count": len(authors_info),
                   "dict": default_dict,
                   "js_dict": json.dumps(js_dict),
                   "journal_lst": journal_lst[:-2]})
