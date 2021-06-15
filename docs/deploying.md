# Deploying Wahlfang for Production Use

## Install
To install `wahlfang` simply install it from PyPi

```shell
$ pip install wahlfang
```

## Database
We recommend setting up a postgresql database for production use, although django allows mysql and sqlite
(please do not use this one for production use, please) as well. All database backends supported by django
can be used.

## Settings
Wahlfang can be customized using a configuration file at `/etc/wahlfang/settings.py`. 
The path to this configuration file can be changed by setting the `WAHLFANG_CONFIG` environment variable.

A starting point for a minimum production ready settings file can be found [here](settings.py).

After configuring your database make sure to not forget the required database migrations. Simply run

```shell
$ wahlfang migrate
```

After configuring a suitable `STATIC_ROOT` for your deployment which will contain all static assets served by your webserver run 

```shell
$ wahlfang collectstatic
```

### Management commands
You can create a local election management user with:
```bash
$ wahlfang create_admin
```

### Non-Python Requirements

* Nginx
* Daphne
* Redis
* PDFLatex (only needed when you want to print invite lists for elections)

## Nginx + Daphne

### `daphne.service`

```ini
[Unit]
Description = daphne daemon
After = network.target

[Service]
User = www-data
Group = www-data
RuntimeDirectory = daphne
ExecStart = daphne wahlfang.asgi:application
ExecReload = /bin/kill -s HUP $MAINPID
KillMode=mixed
TimeoutStopSec=5
PrivateTmp=true

[Install]
WantedBy=multi-user.target
```

Example nginx config.

### `nginx`

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
        # as configured in settings.py under STATIC_ROOT
        alias /var/www/wahlfang/static;
    }

    location /media {
        # as configured in settings.py under MEDIA_ROOT
        alias /var/www/wahlfang/media;
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

## Periodic tasks
Create a systemd service to run periodic tasks such as sending reminder e-mails for elections where this feature has
been enabled.

### `wahlfang-reminders.timer`
```ini
[Unit]
Description=Wahlfang Election Reminders Timer

[Timer]
OnCalendar=*:0/10

[Install]
WantedBy=timers.target
```

### `wahlfang-reminders.service`
```ini
[Unit]
Description=Wahlfang Election reminders

[Service]
# the specific user that our service will run as
User = www-data
Group = www-data
ExecStart = wahlfang process_reminders
TimeoutStopSec = 5
PrivateTmp = true
```
