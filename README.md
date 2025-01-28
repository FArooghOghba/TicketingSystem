# ticketing_system

## project setup

1- complete cookiecutter workflow (recommendation: leave project_slug empty) and go inside the project
```
cd ticketing_system
```

2- SetUp venv
```
virtualenv -p python3.10 venv
source venv/bin/activate
```

3- install Dependencies
```
pip install -r requirements_dev.txt
```

4- create your env
```
.env
```

5- Create tables
```
python manage.py migrations
python manage.py migrate
```

6- run the project
```
python manage.py runserver
```