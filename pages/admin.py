from django.contrib import admin

# Register your models here.
from .models import Article, Tag, ArticleTags


class TagsInlineAdmin(admin.StackedInline):
    model = Article.tags.through
    extra = 0 # 去掉空行
    can_delete = True # 让文章关联的标签可以移除

class ArticleAdmin(admin.ModelAdmin):
    # save_on_top = True
    fieldsets = [
        (None, {'fields': ['title', 'content', 'create_time', 'upate_time']}),
    ]
    readonly_fields = ['create_time', 'upate_time'] # 只读字段
    # show_change_link = True
    inlines = (TagsInlineAdmin,)

admin.site.register(Article, ArticleAdmin)
admin.site.register(Tag)
# admin.site.register(ArticleTags)