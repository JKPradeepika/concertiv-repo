PROJECTS_DIR=/var/lib/django

if [ ! -d "$PROJECTS_DIR" ]; then
  mkdir $PROJECTS_DIR
fi;

sudo shopt -s extglob

sudo rm -rf $PROJECTS_DIR/komodo-backend/.env
sudo rm -rf $PROJECTS_DIR/komodo-backend/.env.template
sudo rm -rf $PROJECTS_DIR/komodo-backend/.github
sudo rm -rf $PROJECTS_DIR/komodo-backend/.gitignore
sudo rm -rf $PROJECTS_DIR/komodo-backend/.flake8
