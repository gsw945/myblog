from django.contrib import admin

# Register your models here.
from django.db import models
from martor.widgets import AdminMartorWidget
from django.urls import reverse
from django.utils.html import format_html

from .models import (
    Article, Tag, ArticleTags, ArticleAnalysis, Message, AccessAnalysis,
    ToolCategory, Tool,
)


class TagsInlineAdmin(admin.StackedInline):
    model = Article.tags.through
    extra = 0 # 去掉空行
    can_delete = True # 让文章关联的标签可以移除

class ArticleAdmin(admin.ModelAdmin):
    # save_on_top = True
    fieldsets = [
        (None, {'fields': ['title', 'content', 'visit_link', 'create_time', 'upate_time']}),
    ]
    readonly_fields = ['visit_link', 'create_time', 'upate_time'] # 只读字段
    list_display = ['title', 'visit_link', 'upate_time'] # 列表显示字段
    # show_change_link = True
    inlines = (TagsInlineAdmin,)
    formfield_overrides = {
        models.TextField: {'widget': AdminMartorWidget},
    }
    search_fields = ['title', 'content']  # 搜索字段

    def get_ordering(self, request):
        '''重写排序'''
        return [
            '-upate_time'
        ]
    
    # 访问地址
    def visit_link(self, obj):
        if obj.id is not None:
            url = reverse('pages:detail', args=(obj.id,))
            return format_html('<a href="{url}">{url}</a>', url=url)
        return '-'
    visit_link.allow_tags = True
    visit_link.short_description = '访问地址'

    # 重写显示字段
    def get_fieldsets(self, request, obj=None):
        if obj is None:
            # 添加新文章页面，只显示 title和content
            return [
                (None, {'fields': ['title', 'content']}),
            ]
        return super(ArticleAdmin, self).get_fieldsets(request, obj=obj)

class ArticleAnalysisAdmin(admin.ModelAdmin):
    fieldsets = [
        (None, {'fields': ['article', 'client_ip', 'is_routable', 'access_time']}),
    ]
    readonly_fields = ['article', 'client_ip', 'is_routable', 'access_time'] # 只读字段
    list_display = ['article', 'client_ip', 'is_routable', 'access_time'] # 列表显示字段

admin.site.register(Article, ArticleAdmin)
admin.site.register(Tag)
admin.site.register(ArticleAnalysis, ArticleAnalysisAdmin)
# admin.site.register(ArticleTags)

class MessageAdmin(admin.ModelAdmin):
    fieldsets = [
        (None, {'fields': ['email', 'content', 'reply', 'create_time']}),
    ]
    readonly_fields = ['email', 'reply', 'create_time'] # 只读字段
admin.site.register(Message, MessageAdmin)

class AccessAnalysisAdmin(admin.ModelAdmin):
    fieldsets = [
        (None, {'fields': [
            'regular', 'uid', 'method', 'url', 'referer', 'remote_addr', 'x_real_ip',
            'x_forwarded_for', 'accept_language', 'host', 'remote_host', 'remote_user',
            'user_agent', 'x_requested_with', 'dt_str', 'access_time'
        ]}),
    ]
    readonly_fields = [
        'regular', 'uid', 'method', 'url', 'referer', 'remote_addr', 'x_real_ip',
        'x_forwarded_for', 'accept_language', 'host', 'remote_host', 'remote_user',
        'user_agent', 'x_requested_with', 'dt_str', 'access_time'
    ] # 只读字段
admin.site.register(AccessAnalysis, AccessAnalysisAdmin)

class ToolCategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'index', 'display']

    def get_ordering(self, request):
        return ['index', '-display']

    def get_form(self, request, obj=None, **kwargs):
        '''新建表单重写'''
        form = super(ToolCategoryAdmin, self).get_form(request, obj, **kwargs)
        # 读取最大排序index
        max_index = ToolCategory.objects.values('index').order_by('-index').first() or {}
        # 设置index默认值
        form.base_fields['index'].initial = max_index.get('index', 0) + 1
        return form

admin.site.register(ToolCategory, ToolCategoryAdmin)
class ToolAdmin(admin.ModelAdmin):
    list_display = ['name', 'index', 'display']

    def get_ordering(self, request):
        return ['index', '-display']

    def get_form(self, request, obj=None, **kwargs):
        form = super(ToolAdmin, self).get_form(request, obj, **kwargs)
        max_index = Tool.objects.values('index').order_by('-index').first() or {}
        form.base_fields['index'].initial = max_index.get('index', 0) + 1
        return form

    class Media:
        from django.conf import settings
        static_url = getattr(settings, 'settings.STATIC_URL', '/static')
        extend = True
        js = [
            static_url + '/admin/tool.js',
        ]
admin.site.register(Tool, ToolAdmin)
