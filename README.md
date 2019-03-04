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