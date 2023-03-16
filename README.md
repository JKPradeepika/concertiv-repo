# Komodo

Komodo is Concertiv's unified contract management and workflow application, designed to replace Analytics and Profiler. This is the backend portion, to be used in tandem with the komodo-frontend project

**NOTE: When we reference "the 1pass entry", we are referring to the following URL: <https://start.1password.com/open/i?a=TLAS4ITBKJHJFPWAJ6DHXD72TU&v=upyj7hzuf5c4ncwyd5vnn3lcxy&i=giqvggjoh73iwwrazcjppxgzqa&h=kbbpartners.1password.com>**

👆 To open that URL, you must be part of the Komodo Engineering group on 1pass.

## First-time Setup

### env changes

1. create a copy of .env.template and rename it to .env
2. add/edit the secret keys found in the 1pass entry

### local db

1. download and install gresql: <https://www.postgresql.org/download/macosx/>
*** be sure you also allow that installer to download pgadmin4
2. open pgadmin4. left click Servers. you should see PostgreSQL 15 with a postgres database. this shows postgresql is running locally.
3. let's create a login within pgadmin: open Servers -> PostgreSQL 15 -> right click Login/Group Roles -> create -> name dba -> password dba -> all privileges
4. rightclick databases in local database server -> create -> name komodo-dev-local -> owner dba
5. now, you'll want a local db with data from the komodo site running the dev branch (frontend is currently komodo-dev.concertiv.com). to start this, let's connect to pgadmin to devsite db...
6. within pgadmin, rightclick pgAdmin Servers -> Register -> Server
7. For "name", it's up to you. something descriptive like "komodo devsite db" is recommended. this is your local name for the remote database server that holds the komodo_dev database.
8. Navigate to the connection tab. The hostname and password for the devsite db can be found in the 1pass entry. Click Save at the bottom.
9. now that you are connected to the devsite db in pgadmin, let's make a backup of the devsite db data: under komodo debsite db -> databases, right click komodo_dev -> Backup -> choose filename, format tar, and backup
10. let's create a new local database to be seeded from your backup. right click your new database -> restore -> filename is the backup file you created earlier -> save
11. now, we need to be sure that when you run the komodo-backend repo locally, it connects to your newly created local db. We do this using entries in your .env file:
    - DB_NAME=komodo-dev-local (or whatever you called it)
    - DB_USER=dba
    - DB_PASSWORD=dba
    - DB_HOST=localhost
    - DB_PORT=5432
12. good to go! you have a local database with db data, and you've setup your local komodo-backend project to reach that database. if you ever need new data from the devsite, repeat the backup -> restore steps to overwrite your local database data.

### terminal

Pre-requisite: make sure you have homebrew installed. Their site shows their current installation command at the top: <https://brew.sh/>

1. open a terminal and cd into your komodo-backend dir
2. `brew install virtualenv`
3. `virtualenv venv`
4. `pip install -r requirements.txt`

## Every-time Setup

### every-time database

if you need to...

- migrate your database:  `python3 manage.py migrate`
- create a new migration: `python3 manage.py makemigrations --name "name_of_new_migration"`
- create a superuser: `python3 manage.py createsuperuser`
- create some other record: use the django admin panel! after starting the backend project, navigate to <http://localhost:8000/admin/>. If your database has devsite data, you can login using the info in the 1pass entry. otherwise, you need to create a superuser to have a login. After logging in, you can easily create a record in any table you wish.

### every-time terminal

1. open a terminal and `cd` into your komodo-backend dir
2. `export DJANGO_SETTINGS_MODULE=komodo_backend.settings` [NOTE: we do this because that's where settings.py resides]
3. `source venv/bin/activate`

You can now...

- start the backend project: `python3 manage.py runserver`
- lint the project: `nox -rs lint`
- fix common lint issues: `nox -rs lint:fix`
- run our test suite:  `nox -rs test`
- format code using black: `nox -rs format`

## Remote Deployment

deployment is currently manual; automatic deployments are TBD. Instructions below on manual deployment

1. login to aws via <https://d-9067b99a18.awsapps.com/start/>
2. left click the Komodo AWS account to drop down its accordion content
3. click "Management console" to login
4. Search for and open EC2
5. Open "Instances". Left click the table row corresponding to the env you are deploying to, then click the "Connect" button that appears above the table of instances
6. On the "Connect to instance" window that appears, change nothing; just click "Connect" in the bottom right
7. you are now in a terminal on the remote instance. run `cd /var/lib/django/komodo-backend` in this terminal
8. in the same terminal, run `source venv/bin/activate`
9. `git pull`
10. `python3 manage.py migrate`
11. `sudo systemctl restart gunicorn`
12. deployment is now done. navigate to the relevant url and touch test for confirmation: check that the swagger docs (/docs) are visible, and that you can see records within django admin (/admin). For example, after deploying to dev, check <https://komodo-dev-api.concertiv.com/docs> and <https://komodo-dev-api.concertiv.com/admin>
