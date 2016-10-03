# WritingFeedback
- a research project which crowdsources structural feedbacks for facilitating ESL writing

### How to handle database migrations (by [Flask-Migrate](http://flask-migrate.readthedocs.io/en/latest/) )
- please make sure "environment variables ENV=DEVELOPMENT", which means local database and local server
- init database at *local side*
> python manage.py db init  #only do it at first time
> python manage.py db migrate
> python manage.py db upgrade
- if database scheme changes, do database migration and update
> python manage.py db migrate
> python manage.py db upgrade

- push migrations folder to *server*
> git add migrations/*
> git commit "db migrations"
> git push origin master

- only run db upgrade at remote server
> heroku run python manage.py db upgrade

### How to import local files into remote database
- setup local environment variables
> export ENV=TESTING
> export DATABASE_URL=<db_URL>
> python manage.py import_articles

### How to deal with out of sync between remote db and local db
- check the current version of both databases
- export ENV=DEVELOPMENT
> python manage.py db current
> heroku run python manage.py db current

- check the history of database
> python manage.py db history

-  set the correct version for remote db
> heroku run python manage.py db stamp HEAD or
> heroku run python manage.py db stamp <revision> #Sets the revision in the database to the one given as an argument, without performing any migrations.
> heroku run python manage.py db upgrade

### How to test workflow on mturk sandbox?
##### Local server testing (local db)
##### Remote server testing (remote db)
- check config.txt in mturk folder
> using_sandbox: true
> hostname: https://writingfeedback.herokuapp.com
- check environment variables “ENV” and “DATABASE_URL”
> export ENV=TESTING #using remote db
> export DATABASE_URL=<db_URL>
- run script in local site (use remote db and mturk config)
> python mturk/workflows.py

----------------------------------------------------------
- python mturk/run_workflow_experiment.py (2016.06 Experiment)
- python mturk/run_workflow_experiment2.py (2016.09 Experiment)
- python mturk/analyze_crowd_data.py (2016.09 Experiment)