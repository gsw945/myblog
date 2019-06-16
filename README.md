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
# if you forget password of one user(eg: "admin"), change password of user "admin"
python manage.py changepassword admin
```

### run
```bash
# start server (use one of below 3 types of wsgi-server:)
# # wsgi-server 1: django server (worst performance)
python manage.py runserver 127.0.0.1:8000
# # wsgi-server 2: tornado (medium performance)
python tornado-server.py
# # wsgi-server 3: hendrix(twisted) (best performance)
python twisted-server.py
# visit http://127.0.0.1:8000/
```

### view user list
enter into Django REPL Shell
```bash
python manage.py shell
```
use Django API to view user list
```python
from django.contrib.auth import get_user_model

User = get_user_model()
print(User.objects.all())
```