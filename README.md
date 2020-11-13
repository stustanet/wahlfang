# Wahlfang

StuStaNet Online Wahl-Tool

## Setup

```bash
$ cd wahlfang
$ pip3 install -r requirements.txt
$ python3 manage.py migrate
```

### Management Access

Creating a local election management user:
```bash
$ python3 manage.py 
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

## Run Development Server
Starting the server:
```bash
$ python3 manage.py runserver
```

If some model changed, you might have make and/or apply migrations again:
```bash
$ python3 manage.py makemigrations
$ python3 manage.py migrate
```
Don't forget to add the new migration file to git. If the CI pipeline fails this is most likely the reason for it.

## Development References

- Django 3: https://docs.djangoproject.com/en/3.0/
