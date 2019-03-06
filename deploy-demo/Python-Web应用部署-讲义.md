# Python-Web应用部署步骤

> 假设:
> * 操作系统为原生`Ubuntu 18.04 LTS`
> * 当前登录用户为`xyz`
> * Web程序目录: `/home/xyz/myblog`
> * 虚拟环境运行启动脚本: `/home/xyz/runinenv.sh`

* `/home/xyz/runinenv.sh`内容如下:
    ```shell
    #!/bin/bash
    export SOME_ENV=test-message

    VENV=$1
    if [ -z $VENV ]; then
    echo "usage:runinenv [virtualenv_path] CMDS"
    exit 1
    fi
    source ${VENV}/bin/activate
    shift 1
    echo "Executing $@ in ${VENV}"
    exec "$@"
    deactivate
    ```

---

1. 安装必须的软件
    ```shell
    sudo apt-get install python3-pip virtualenv -y
    sudo apt-get install vim -y
    sudo apt-get install nginx supervisor -y
    ```
2. 创建虚拟环境、安装包、测试程序
    ```shell
    cd ~
    virtualenv v3web --python=python3
    
    source /home/xyz/v3web/bin/activate
    pip install Flask flask_sqlalchemy

    cd /home/xyz/myblog
    python index.py

    deactivate
    ```
3. 使用supervisor管理进程（后台运行）
    ```shell
    cd /etc/supervisor/conf.d/
    vim demo.conf
    ```
    `/etc/supervisor/conf.d/demo.conf`内容如下:
    ```
    [program:demo]
    user=xyz
    directory=/home/xyz/myblog/
    command=/bin/bash /home/xyz/runinenv.sh /home/xyz/v3web python /home/xyz/myblog/index.py
    autostart=true
    autorestart=true
    startsecs=5
    stopsignal=HUP
    stopasgroup=true
    stopwaitsecs=5
    stdout_logfile_maxbytes=20MB
    stdout_logfile=/var/log/supervisor/%(program_name)s-out.log
    stderr_logfile_maxbytes=20MB
    stderr_logfile=/var/log/supervisor/%(program_name)s-err.log
    ```
    配置要点：
    - `[program:<名称>]`
    - `user=<运行用户>`
    - `directory=<启动目录>`
    - `command=<运行的命令>`
    - `environment=<环境变量>`
        参考: [Supervisor and Environment Variables](https://stackoverflow.com/questions/12900402/supervisor-and-environment-variables/19611920#19611920)
4. supervisor管理命令
    ```shell
    # 重新加载配置
    sudo supervisorctl reload
    # 查看进程状态
    sudo supervisorctl status
    # 停止/启动/重启某个进程（此处为demo）
    sudo supervisorctl stop/start/restart demo
    ```
5. Linux基础命令
    ```shell
    # 查看和python相关的tcp连接
    netstat -antp | grep python
    # 查看和python相关的进程
    ps uax | grep python
    # 杀死指定名称的进程（此处为python）
    sudo pkill python
    ```
6. 配置nginx
    ```shell
    cd /etc/nginx/conf.d/
    sudo vim demo.conf
    ```
    `/etc/nginx/conf.d/demo.conf`内容如下:
    ```
    server {
        listen 80;
        listen [::]:80;
        server_name localhost;

        location / {
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header Host $http_host;
            proxy_set_header X-NginX-Proxy true;

            proxy_pass http://127.0.0.1:5000/;
            # proxy_pass http://10.0.0.10:8999/;
            proxy_redirect off;
        }
        
        location /static/ {
            alias /home/xyz/myblog/static/;
        }
    }
    ```
7. nginx管理命令
    ```shell
    # 重启nginx服务（会重新加载配置文件）
    sudo service nginx restart
    # 启动、停止服务器
    sudo service nginx start/stop
    ```
8. nginx静态文件403解决方案
    修改nginx配置文件(改完了需要重启)
    ```shell
    vim /etc/nginx/nginx.conf
    ```
    将如下的行(nginx运行用户默认为`www-data`)
    ```
    user www-data;
    ```
    改为(将nginx运行用户改为`root`)
    ```
    user root;
    ```
    一般情况下，也将nginx运行用户改为当前用户（此处为`xyz`）
    ```
    user xyz;
    ```
    重启服务器
    ```shell
    sudo service nginx restart
    ```
9. 添加用户, 并添加到sudo组
    ```shell
    # 创建名为pyuser的用户
    adduser pyuser
    # 将用户pyuser添加到sudo组里
    usermod -a -G sudo pyuser
    ```