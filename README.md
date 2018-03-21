# README

This repo contains a REST API that acts as an aggregator for both bitbucket and github accounts. It provides an interface to create an API user, and attach bitbucket/github users to an API user.

## Environment Setup

This assignment is implemented in python 3.6. Assuming you have 3.6 on your path you may run the following to create an environment to run the code:

```
# create a virtual environment
# may need to use python3 instead of python for the following command
python -m venv ./venv
source ./venv/bin/activate
pip install -r requirement.txt
```

## Running tests

Assuming you have run the previous set up steps, you can use the following to run the test suite:

```
source ./venv/bin/activate
python tests.py
```

## Running the REST API

The API is written as a flask application, which you can run with the following command:

```
source ./venv/bin/actviate
python main.py
```

There is a file titled `curl_tests.sh` that will exercise different tasks against the API.

## Notes on implementation

Due to the fact that some of the APIs provided by both github and bitbucket don't provide an easy way to aggregate beyond paginating through all results, it's possible to hit rate limits when exercising the API. You can overcome this by setting an environment variable `GITHUB_OAUTH_TOKEN` before you run the flask application. In testing I did not hit the bitbucket rate limits.

In order to reduce dependencies to run the application, I implemented a 'db' module that acts as a mini ORM. Any time the flask application is shut down the 'database' effectively goes away'. In a real application I would use something like postgres + sqlalchemy which could have real many-to-many relationships and support multiple processes/multithreading. Given that the API operations against bitbucket are expensive, the `POST` methods against those APIs only remove the relation between an API user and a github/bitbucket profile.

