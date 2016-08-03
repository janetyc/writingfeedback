# WritingFeedback
- a research project which collects structure feedbacks for improving writing organization

### How to handle database migrations (by [Flask-Migrate](http://flask-migrate.readthedocs.io/en/latest/) )
- init database at local side
> python manage.py db init  #only do it at first time
> python manage.py db migrate
> python manage.py db upgrade
- if database scheme changes, do database migration and update
> python manage.py db migrate
> python manage.py db upgrade

- push migrations folder to server
 > git add migrations/*
> git push origin master

- only run db upgrade at remote server
> heroku run python manage.py db upgrade

### How to import local files into remote database
- setup local environment variables
> export ENV=TESTING
> export DATABASE_URL=<db_URL>
> python manage.py import_articles
