# Minimalistic Issue Tracker README

## Overview
Very simple issue tracker that lacks a lot of features.

## Requirements
No other dependencies except Django 2.0 required.

## Installation
### Create virtual environment
If you want to use globally installed python3, skip this step. Otherwise, run:
> virtualenv -p /usr/bin/python3 venv

To create python3 virtual environment. If necessary, replace /usr/bin/python3 with any other path to python3 interpreter, and venv to any other directory where vritual envrinment will reside.

Activate new virtual environment:
>$ source venv/bin/activate

### Install Django 2.0
> $ pip install django>=2

### Create database and Administrator user
The project comes with no database. To create one, run:
> $ ./manage.py migrate

The SQLite database will be created and stored in ~/.min_it/db.sq3.

To create Administrator user, run:
> $ ./manage.py createsuperuser

and follow the instructions.

## Demo
To generate demo data, run:
> $ ./manage.py gendemodata

By default this command creates 10 staff users, 10 super-users and 1000 of issues. You may change this behaviour by passing optional arguments (--num_staffusers, --num_superusers, --num_issues).

If you just want to check how the project looks like in a web-browser, and don't really want to go through the whole installation process, you may simply use Django developement server.
Run the following command:
> $ ./manage.py runserver

which will start a server listening on localhost:8000. Then open http://localhost:8000/ in your web-browser, and login using the Administrator credentials.

## Running tests
There are few tests covering a small part of project functionality. To execute them, run:
> $ ./manage.py test

## Deployment
If you want to run this application using production-class application server (e.g., uWSGI, Gunicorn), please refer to Django deplyment guide (https://docs.djangoproject.com/en/2.0/howto/deployment/).
