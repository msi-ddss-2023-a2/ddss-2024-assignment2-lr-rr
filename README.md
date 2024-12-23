# MSI DDSS - Assignment 2

The code and resources available in this repository are to be used in the scope of the _DDSS_ course.

## Overview of the Contents

In this repository you will find the supporting resources for Assignment 2 of MSI-DDSS 2024/2025.

- [**`PostgreSQL`**](postgresql) - Database ready to run in a docker container with or without the help of the docker-compose tool;
- [**`Python`**](python) - Source code of web application template in python with Docker container configured. Ready to run in docker-compose with PostgreSQL
  - [`app/`](python/app) folder is mounted to allow developing with container running
- [**`interfaces`**](interfaces) - the html interfaces mentioned in the assignment description. Necessary html interfaces in case other language/framework is adopted.
- [**`docker-compose`**](.) - Files that start the demo Python, Java, NodeJS and php applications together with a PostgreSQL database;

## Requirements

To execute this project it is required to have installed:

- `docker`
- `docker-compose`

## Development

You should select one of the options or add your own.
Then you just need to develop inside the folder and run the script (e.g. [`./docker-compose-php-psql.sh`](docker-compose-php-psql.sh)) to have both the server and the database running.

[`Python`](python) allow you to be developing while the containers are running, and the sources are continuously being integrated.

**Delete everything you are not planing to you in your assignment.**

In `Linux` deployments you must confirm that you have `docker` installed and running, use the command `ps ax | grep dockerd` to check if `dockerd` is running, which is the process that manages containers.
You should run your commands as superuser, and therefore you should prefix your `docker`/`docker-compose` commands with `sudo` (e.g. `sudo ./docker-compose-php-psql.sh`).

## Web browser access

After the required commands and having started the web application, they will available on your browser at:

- Python version: https://localhost:443;

# Authors

- Nuno Antunes <nmsa@dei.uc.pt>
- Marco Vieira <mvieira@dei.uc.pt>

# Developers

- Rui Rodrigues <ruirodrigues@student.dei.uc.pt>
- Luís Reis <luisreis@student.dei.uc.pt>
