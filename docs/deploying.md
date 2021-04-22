## Deploying Wahlfang for Production Use
Clone the repository. This guide will assume it has been cloned to `/srv/wahlfang/repo`. 
If you choose some another location make sure to adapt all paths in the following config files.

Additionally this guide uses `virtualenv` to manage python dependencies. If you cannot or do not want to use it
you'll have to adapt some of the following parts.

```bash
mkdir /srv/wahlfang
cd /srv/wahlfang
git clone https://gitlab.stusta.de/stustanet/wahlfang.git repo
virtualenv -p /usr/bin/python3 venv
source venv/bin/activate
pip install repo/requirements.txt
```

### Configuration
TODO

### Database
We recommend setting up a postgresql database for production use, although django allows mysql and sqlite 
(please do not use this one for production use, please) as well.

### E-Mail
TODO

### Periodic tasks
Create a systemd service to run periodic tasks such as sending reminder e-mails for elections where this feature has
been enabled.

#### `wahlfang-reminders.timer`
```ini
[Unit]
Description=Wahlfang Election Reminders Timer

[Timer]
OnCalendar=*:0/10

[Install]
WantedBy=timers.target
```

#### `wahlfang-reminders.service`
```ini
[Unit]
Description=Wahlfang Election reminders

[Service]
# the specific user that our service will run as
User=wahlfang
Group=wahlfang
Environment=DJANGO_SETTINGS_MODULE=wahlfang.settings
WorkingDirectory=/srv/wahlfang/repo/
ExecStart=/srv/wahlfang/venv/bin/python manage.py process_reminders
TimeoutStopSec=5
PrivateTmp=true
```

### Nginx + Gunicorn
Example gunicorn systemd service. Assumes wahlfang has been cloned to `/srv/wahlfang/repo` with a virtualenv containing
all requirements and gunicorn in `/srv/wahlfang/venv`.

#### `gunicorn.service`
```ini
[Unit]
Description=gunicorn daemon
Requires=gunicorn.socket
After=network.target

[Service]
Type=notify
User=wahlfang
Group=wahlfang
Environment=DJANGO_SETTINGS_MODULE=wahlfang.settings
RuntimeDirectory=gunicorn
WorkingDirectory=/srv/wahlfang/repo/
ExecStart=/srv/wahlfang/venv/bin/gunicorn wahlfang.wsgi
ExecReload=/bin/kill -s HUP $MAINPID
KillMode=mixed
TimeoutStopSec=5
PrivateTmp=true

[Install]
WantedBy=multi-user.target
```

#### `gunicorn.socket`
A corresponding systemd.socket file for socket activation.

```ini
[Unit]
Description=gunicorn socket

[Socket]
ListenStream=/run/gunicorn.sock
# Our service won't need permissions for the socket, since it
# inherits the file descriptor by socket activation
# only the nginx daemon will need access to the socket
User=www-data

[Install]
WantedBy=sockets.target
```

Example nginx config.

#### `nginx`
```
server {
    listen 80 default_server;
    listen [::]:80 default_server;
    
    return 301 https://$host$request_uri;
}

server {
    listen 443 ssl http2 default_server;
    listen [::]:443 ssl http2 default_server;
    ssl_certificate /path/to/ssl/fullchainfile;
    ssl_certificate_key /path/to/ssl/key;
    charset utf-8;

    location /static {
        alias /var/www/wahlfang/static;
    }

    location /media {
        alias /var/www/wahlfang/media;
    }

    location / {
        proxy_pass http://unix:/run/gunicorn.sock;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
	    proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    }
}
```
