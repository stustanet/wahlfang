# Wahlfang
> A self-hostable online voting tool developed to include all the 
> features you would need to hold any online election you can dream of

Developed by [StuStaNet](https://stustanet.de) Wahlfang is a small-ish Django project
which aims at being an easy to use solution for online elections. From simple one-time
votes about where to grab a coffee to large and long meetings with multiple different 
votes and elections - Wahlfang does it all.

If you would like a new feature or have a bug to report please open an [issue](https://github.com/stustanet/wahlfang/issues).

## Getting Started
To setup your own wahlfang instance for productive use see [deploying](docs/deploying.md).

### Metrics

In the default configuration wahlfang exports some internal application statistics as [Prometheus](https://prometheus.io/) 
metrics at the endpoint `/metrics`. This behaviour can be turned off by settings `EXPORT_PROMETHEUS_METRICS = False`
in the application settings.

We use the [django-prometheus](https://github.com/korfuri/django-prometheus) project to export our exports.

## Contributing
To just get the current version up and running simply
```bash
$ git clone https://gitlab.stusta.de/stustanet/wahlfang.git
$ cd wahlfang
$ pip3 install -r requirements.txt
$ pip3 install -r requirements_dev.txt
$ export WAHLFANG_DEBUG=True
$ export PYTHONPATH="$PYTHONPATH:."
$ python3 wahlfang/manage.py migrate
$ python3 wahlfang/manage.py runserver localhost:8000
```

Creating a local election management user:
```bash
$ python3 wahlfang/manage.py create_admin
```

Login to the management interface running at [http://127.0.0.1:8000/management/](http://127.0.0.1:8000/management/).

Run the linting and test suite
```bash
$ make lint
$ make test
```

If some model changed, you might have to make and/or apply migrations again:
```bash
$ python3 wahlfang/manage.py makemigrations
$ python3 wahlfang/manage.py migrate
```
Don't forget to add the new migration file to git. If the CI pipeline fails this is most likely the reason for it.

## Releasing
The release process is automated in the gitlab ci.

To make a new release bump the package version number in `wahlfang.__init__.py` and tag the commit with the same version
number. The CI will then build the package, publish it as a gitlab release and push it to pypi.

The pypi credentials must be set in the gitlab CI settings via the env variables `TWINE_USERNAME` and `TWINE_PASSWORD`.

## Development References

- Django 3: https://docs.djangoproject.com/en/3.2/
