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

### Non-Python Requirements

* Nginx
* Daphne
* Redis
* PDFLatex (only needed when you want to print invite lists for elections)

### Channels integration

In settings.py change the django channels' backend to redis in order to have self refreshing pages and other dynamic
frontend features

```python
CHANNEL_LAYERS = {
  "default": {
    "BACKEND": "channels_redis.core.RedisChannelLayer",
    "CONFIG": {
      "hosts": [("127.0.0.1", 6379)],
    },
  },
}
```

### Configuration

* `EXPORT_PROMETHEUS_METRICS`: Export application statistics such as http request duration / latency. This will also
  export the amount of manager accounts, the amount of sessions and the amount of elections. The metrics will be
  reported in /metrics.
* `URL`: Base URL address such as `vote.stusta.de`
* `AUTHENTICATION_BACKENDS`: Comment out `management.authentication.ManagementBackendLDAP` if you do not want to use
  LDAP as authentication backend for management account. Otherwise have a look at the `LDAP_*` options in the
  configuration.

### Database
We recommend setting up a postgresql database for production use, although django allows mysql and sqlite 
(please do not use this one for production use, please) as well.

### E-Mail

In order to send out session invitation you need to configure a SMTP sever. Have a look at the
[django doku](https://docs.djangoproject.com/en/3.2/topics/email/) for reference on how to configure your SMTP server in
the django doku.

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
User = wahlfang
Group = wahlfang
Environment = DJANGO_SETTINGS_MODULE=wahlfang.settings
WorkingDirectory = /srv/wahlfang/repo/
ExecStart = /srv/wahlfang/venv/bin/python manage.py process_reminders
TimeoutStopSec = 5
PrivateTmp = true
```

### Nginx + Daphne

Example daphne systemd service. Assumes wahlfang has been cloned to `/srv/wahlfang/repo` with a virtualenv containing
all requirements and daphne in `/srv/wahlfang/venv`.

#### `daphne.service`

```ini
[Unit]
Description = daphne daemon
After = network.target

[Service]
User = wahlfang
Group = wahlfang
Environment = DJANGO_SETTINGS_MODULE=wahlfang.settings
RuntimeDirectory = daphne
WorkingDirectory = /srv/wahlfang/repo/
ExecStart = /srv/wahlfang/venv/bin/daphne wahlfang.asgi:application
ExecReload = /bin/kill -s HUP $MAINPID
KillMode=mixed
TimeoutStopSec=5
PrivateTmp=true

[Install]
WantedBy=multi-user.target
```

Example nginx config.

#### `nginx`

```
upstream daphne_server {
    server localhost:8000;
}
server {
    listen 80 default_server;
    listen [::]:80 default_server;
    
    server_name _;
    
    return 301 https://$host$request_uri;
}

server {
    listen 443 ssl http2 default_server;
    listen [::]:443 ssl http2 default_server;
    ssl_certificate /path/to/ssl/fullchainfile;
    ssl_certificate_key /path/to/ssl/key;
    charset utf-8;

    location /static {
        alias /srv/wahlfang/static;
    }

    location /media {
        alias /srv/wahlfang/media;
    }

    location / {
        proxy_pass http://daphne_server;
        
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
	    proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    }
}
```
