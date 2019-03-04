# Step-1
```bash
# 创建文件夹
mkdir myblog
# 创建项目
django-admin startproject main myblog
# 进入项目目录
cd myblog
# 数据迁移（创建、修改数据库表）
python manage.py migrate
# 创建超级管理员账户（admin/admin@123）
python manage.py createsuperuser
# 启动Web服务器
python manage.py runserver 127.0.0.1:8282
```

# Step-2
```bash
# 创建页面应用
python manage.py startapp pages
# 创建模型迁移文件
python manage.py makemigrations pages
# 数据迁移（创建、修改数据库表）
python manage.py migrate
```

# Step-3
```bash
# 进入Django-Shell(便于执行数据库操作)
python manage.py shell
```
```python
# 数据库操作代码片段
from pages.models import Article, Tag, ArticleTags

# 创建文章
article = Article(title='Python入门', content='Hello Python')
article.save() # 保存
# 查询文章
article = Article.objects.filter(id=1).first()

# 创建标签1
tag1 = Tag(name='Python')
tag1.save() # 保存
# 查询标签1
tag1 = Tag.objects.filter(id=1).first()

# 创建标签2
tag2 = Tag(name='Hello')
tag2.save() # 保存
# 查询标签2
tag2 = Tag.objects.filter(id=2).first()

# 创建文章-标签1关联
at1 = ArticleTags(article=article, tag=tag1)
at1.save() # 保存

# 创建文章-标签2关联
at2 = ArticleTags(article=article, tag=tag2)
at2.save() # 保存


# 查询文章所有关联的标签
article.tags.all()
# 查询标签1所有关联的文章
tag1.articles.all()
# 查询标签2所有关联的文章
tag2.articles.all()
# 查询所有的文章-标签关联
ArticleTags.objects.filter(article=article).all()
```