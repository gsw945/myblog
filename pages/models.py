from django.db import models

# Create your models here.
from django.utils import timezone

class Article(models.Model):
    title = models.CharField('标题', max_length=200)
    content = models.TextField(verbose_name='内容')
    create_time = models.DateTimeField('创建时间', default=timezone.now)
    upate_time = models.DateTimeField('最后修改时间', auto_now=True)
    tags = models.ManyToManyField('Tag', through='ArticleTags')

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = '文章'
        verbose_name_plural = '文章'
        app_label = 'pages'

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