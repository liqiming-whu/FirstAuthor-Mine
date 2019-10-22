from django.conf.urls import url
from django.urls import path
from . import views
from . import add_search

app_name = "article"
urlpatterns = [
    path('', views.First_author, name='first'),
    path('title/', views.Article_title, name='title'),
    path('score/', views.author, name='score'),
    path('add_journal/', add_search.add_journal, name='add_journal'),
    path('edit_journal/', add_search.edit_journal, name='edit_journal'),
    path('del_journal/', add_search.del_journal, name='del_journal'),
    path('add_article/', add_search.add_article, name='add_paper'),
    path('title/<article_pmid>/', views.Article_detail, name='detail'),
    path('author/<author_id>/', views.Author_detail, name='author'),
    path('title/<article_pmid>/result', views.get_result, name='result'),
    path('journal/<article_journal_name>/', views.journal, name='journal'),
    path('topic/<article_subject>/', views.topic, name='topic'),
]
