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

```bash
$ cd wahlfang
$ pip3 install -r requirements.txt
$ python3 manage.py migrate
$ python manage.py runserver
```

### Management Access

Creating a local election management user:
```bash
$ python3 manage.py crreate_admin
```

The admin interface is accessible at [http://127.0.0.1:8000/admin/](http://127.0.0.1:8000/admin/).
An admin account can also use the management interface 
[http://127.0.0.1:8000/management/](http://127.0.0.1:8000/management/).


### Generating Test Data

Either via the [management interface](http://127.0.0.1:8000/management/) with the credential of the superuser created
above or by using the following (old) method:

Create an election:
```bash
$ python3 manage.py create_election --title "Hausadminwahl SS20 im Testhaus" --max-votes-yes 2
```

Create a voter:
```bash
$ python3 manage.py create_voter --election_id 1 --voter_id 1337
```

You can then login with the printed access code.

## Contributing
Starting the server:
```bash
$ python3 manage.py runserver
```

If some model changed, you might have to make and/or apply migrations again:
```bash
$ python3 manage.py makemigrations
$ python3 manage.py migrate
```
Don't forget to add the new migration file to git. If the CI pipeline fails this is most likely the reason for it.

## Development References

- Django 3: https://docs.djangoproject.com/en/3.0/
