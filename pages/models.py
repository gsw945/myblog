from django.db import models

# Create your models here.
from django.utils import timezone
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.core.exceptions import ObjectDoesNotExist
from martor.views import MARTOR_MARKDOWNIFY_FUNCTION, import_string
from bs4 import BeautifulSoup
from bs4 import Comment


markdownify = import_string(MARTOR_MARKDOWNIFY_FUNCTION)

class Article(models.Model):
    title = models.CharField('标题', max_length=200)
    content = models.TextField(verbose_name='内容', default=None, blank=True, null=True)
    abstract = models.TextField(verbose_name='摘要', default=None, blank=True, null=True)
    create_time = models.DateTimeField('创建时间', default=timezone.now)
    upate_time = models.DateTimeField('最后修改时间', auto_now=True)
    tags = models.ManyToManyField('Tag', through='ArticleTags')
    
    def __str__(self):
        return self.title

    class Meta:
        verbose_name = '文章'
        verbose_name_plural = '文章'
        app_label = 'pages'

    @property
    def next_article(self):
        try:
            return self.__class__.get_next_by_create_time(self)
        except ObjectDoesNotExist:
            return None

    @property
    def previous_article(self):
        try:
            return self.__class__.get_previous_by_create_time(self)
        except ObjectDoesNotExist:
            return None

    @property
    def analysis_count(self):
        return self.articleanalysis_set.count()

@receiver(post_save, sender=Article, dispatch_uid="update_article_abstract")
def update_article_abstract(sender, instance, **kwargs):
    abstract = markdownify(instance.content)
    soup = BeautifulSoup(abstract, "html.parser")
    exclude_tags = ['style', 'script', 'code']
    for tag in soup(exclude_tags):
        tag.decompose()
    # abstract = soup.get_text() # 方式一（存在多余空白字符）
    abstract = ' '.join(soup.stripped_strings) # 方式一
    abstract = abstract[:100]
    # 保存，但是不触发 post_save 信号
    Article.objects.filter(id=instance.id).update(abstract=abstract)

class Tag(models.Model):
    name = models.CharField('标签名', max_length=30)
    articles = models.ManyToManyField('Article', through='ArticleTags')

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = '标签'
        verbose_name_plural = '标签'
        app_label = 'pages'

class ArticleTags(models.Model):
    article = models.ForeignKey(Article, on_delete=models.CASCADE)
    tag = models.ForeignKey(Tag, on_delete=models.CASCADE)

    def __str__(self):
        return '{0}[{1}]'.format(self.article.title, self.tag.name)

    class Meta:
        verbose_name = '文章标签'
        verbose_name_plural = '文章标签'
        app_label = 'pages'

class ArticleAnalysis(models.Model):
    article = models.ForeignKey(Article, on_delete=models.CASCADE)
    client_ip = models.CharField('访问者IP', max_length=255)
    is_routable = models.BooleanField('是否是可路由')
    access_time = models.DateTimeField('访问时间', default=timezone.now)

    def __str__(self):
        return '{0}[{1}]'.format(self.article.title, self.client_ip)

    class Meta:
        verbose_name = '文章访问统计'
        verbose_name_plural = '文章访问统计'
        app_label = 'pages'
