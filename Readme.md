=========================================

FrxMonExp - Forex Money Experience

Created on, 10 April 2020

Last Updated on Python 3.x.x: 10 May 2020

Last Updated By : Aditya

=========================================

A simple <strong> Web application</strong> which picks currency rates in real time from different websites
and enable users to see all of the currency rates on one single platform.

Steps to Run on 'localhost' Windows platform are given below, However for other platforms check: https://flask.palletsprojects.com
/en/1.1.x/installation/

Steps to follow :
- Import project FrxMonExp and create a virtual environment using terminal: `python3 -m venv venv` for windows
- Activate virtual environment using terminal: `venv\Scripts\activate`
- Use `pip freeze > requirements.txt` to create & see packages used in `requirements.txt` file

**Setup PostgreSQL Database:**

1.) Download PostgreSQL database here: https://www.enterprisedb.com/downloads/postgres-postgresql-downloads, if you use GUI interface for PostgreSQL then while installing skip pgadmin setup.

2.) Download, Run and install pgadmin here: https://www.pgadmin.org/download/pgadmin-4-windows/.

3.) Setup database and create as new database, Name it to '`productcomparision`'.

4.) Use Console and type following commands to create the table and columns:

  NOTE: Make sure your server is turned off at the time you run the below commands
    
  i.) `from product_server import db`, Press `enter`
  
  ii.) `db.createall()`, Press `enter`
    
- Run cmd: `set FLASK_APP = product_server.py` press `enter` then run, cmd: `flask run`
- Visit localhost -> `http://localhost:5000` to see the web application interface


**Deployment to Heroku Cloud Server**

Steps:
- Make a new git repository
- Clone your git repository and put all the project files into this repository
- Install Heroku command line interface (CLI) from https://devcenter.heroku.com/articles/heroku-cli
- In CLI type `cmd: heroku login` then create project using `cmd: heroku create forexmoneyexperience`
- Create DATABASE using `cmd: heroku addons:create heroku-postgresql:hobby-dev --app forexmoneyexperience`
- Get DATABASE_URL using `cmd: heroku config --app forexmoneyexperience`
- Install package `gunicorn` and create a `Procfile` and mention `web: gunicorn --bind 0.0.0.0:$PORT product_server:app`
- Create `runtime.txt` file and mention runtime python version `python-3.7.6` in it
- Add files to git using `cmd: git add. && commit -m "Initial deployment"`
- Create a Heroku git repository `cmd: heroku git:remote -a forexmoneyexperience`
- Push files to Heroku git using `cmd: git push heroku master` which will deploy the application to heroku server
- Now, for creating the tables in DATABASE go to CLI and type `cmd: heroku run python`
- Create table using `cmd: from product_server import db` then `cmd: db.create_all()` and exit the console
- To see the DATABASE use `cmd: heroku pg:psql --app forexmoneyexperience`
- To see all columns from the table use `cmd: SELECT * FROM TABLE_NAME;`
