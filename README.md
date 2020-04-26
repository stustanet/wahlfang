# Wahlfang

StuStaNet Online Wahl-Tool

## Setup

```bash
$ pip3 install -r requirements.txt
```

### Generating Test Data
Create an election:
```bash
python3 manage.py createelection --title "Hausadminwahl SS20 im Testhaus"
```

Create a voter:
```bash
python3 manage.py createvoter --election_id 1 --voter_id 1337
```

You can login with the printed access code.

### Admin Access (optional)

Creating a superuser (for testing):
```bash
$ python3 manage.py createsuperuser
```

The admin interface is accessible at http://127.0.0.1:8000/admin/

## Run Development Server
Starting the server:
```bash
$ python3 manage.py runserver
```

If some model changed, you might have to apply migrations:
```bash
$ python3 manage.py migrate
```

## Development References

- Django 3: https://docs.djangoproject.com/en/3.0/
