from django.urls import path

from . import views
from . import apis

app_name = 'pages'
urlpatterns = [
    path('', views.view_index, name='index'),
    path('article/', views.view_list, name='list'),
    path('article/<int:article_id>', views.view_detail, name='detail'),
    path('copyright/', views.view_copyright, name='copyright'),
    path('about/', views.view_about, name='about'),
    path('message/', views.view_message, name='message'),
    path('search/', views.view_search, name='search'),
    path('analysis/article/', apis.api_article_analysis, name='article_analysis'),
    path('generate-captcha/', apis.api_generate_captcha, name='generate_captcha'),
    path('leave-message/', apis.api_leave_message, name='leave_message'),
]