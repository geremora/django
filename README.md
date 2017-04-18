# CASP Case management
Case management system for Comisión Apelativa del Servicio Público.

## Environmental Variables Setup

```
cp .env.example .env
```

and put the `DATABASE_URL` with your database connection string

## Automatic setup

```
$ pip install -r requirements.txt
$ fab initialsetup
```


## Step-by-step setup

```
$ pip install -r requirements.txt

$ python manage.py syncdb --noinput
$ python manage.py migrate apps.profiles
$ python manage.py migrate apps.contacts
$ python manage.py migrate

$ python manage.py update_permissions

$ python manage.py createcachetable cache_table
```

## Running the test cases

```
python manage.py test
```
