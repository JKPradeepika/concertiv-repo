PROJECT_DIR=/var/lib/django/komodo-backend

# assign ubuntu user group to project
sudo chown -R ubuntu:ubuntu $PROJECT_DIR

# shellcheck disable=SC2164
cd $PROJECT_DIR

# copy .env to project folder
cp ../.env .

# python venv and install dependencies
virtualenv venv
source $PROJECT_DIR/venv/bin/activate
pip install -r $PROJECT_DIR/requirements.txt

# collectstatic and migrations
python3 manage.py migrate
python3 manage.py collectstatic --no-input
python3 manage.py loaddata komodo_backend/fixtures/*.json
sudo systemctl restart gunicorn