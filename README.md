# Wahlfang
> A self-hostable online voting tool developed to include all the 
> features you would need to hold any online election you can dream of

Developed by [StuStaNet](https://stustanet.de) Wahlfang is a small-ish Django project
which aims at being an easy to use solution for online elections. From simple one-time
votes about where to grab a coffee to large and long meetings with multiple different 
votes and elections - Wahlfang does it all.

If you would like a new feature or have a bug to report please open an issue over 
at our [Gitlab](https://gitlab.stusta.de/stustanet/wahlfang/-/issues).

## Getting Started
To just get the current version up and running simply
```bash
$ git clone https://gitlab.stusta.de/stustanet/wahlfang.git
$ cd wahlfang
$ pip3 install -r requirements.txt
$ python3 manage.py migrate
$ python3 manage.py runserver localhost:8000
```

### Management Access

Creating a local election management user:
```bash
$ python3 manage.py create_admin
```

Login to the management interface running at [http://127.0.0.1:8000/management/](http://127.0.0.1:8000/management/).

## Contributing
Install the development requirements in addition to the standard dependencies:
```bash
$ pip3 install -r requirements_dev.txt
```

Run the linting and test suite
```bash
$ make lint
$ make test
```

If some model changed, you might have to make and/or apply migrations again:
```bash
$ python3 manage.py makemigrations
$ python3 manage.py migrate
```
Don't forget to add the new migration file to git. If the CI pipeline fails this is most likely the reason for it.

## Development References

- Django 3: https://docs.djangoproject.com/en/3.0/
