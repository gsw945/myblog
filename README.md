# myblog
Blog by Django

### online version
- https://blog.gsw945.com/

### setup
```bash
# install pip packages
pip install -r requments.txt -i https://pypi.doubanio.com/simple/ --trusted-host pypi.doubanio.com
# database init
python manage.py migrate
# create admin account
python manage.py createsuperuser
```

### run
```bash
# start server
python manage.py runserver 127.0.0.1:8282
# visit http://127.0.0.1:8282/
```