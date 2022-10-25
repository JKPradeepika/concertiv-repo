### Host Python and Dependencies

You can follow below steps to install requirements and libraries. So VS Code doesn't complain about missing imports and stuff.

### Python virtualenv

Install a virtual environment using the correct python version. Run the following from the backend directory:

`python -m venv venv`

Once installed, you can run `venv\Scripts\activate` to enter your virtual environment.

### Install all required packages

To install all packages to run the backend, run the following under your virtual environment:

`pip install -r requirements.txt`

### Setting DJANGO_SETTINGS_MODULE

All backend commands are postfixed with ` --settings CPR.settings.dev`, which can be annoying. To get around this, you can run `export DJANGO_SETTINGS_MODULE=CPR.settings.dev` and then this will set all commands you run in this shell to use the local settings.

### Creating migrations

Create a new set of database migrations for an app with the following command:

`python manage.py makemigrations --settings CPR.settings.dev`

### Applying Migrations

Apply all unapplied migrations with the following command:

`python manage.py migrate --settings CPR.settings.dev`

### Running the server

To run the server, run the following command:

`python manage.py runserver --settings CPR.settings.dev`