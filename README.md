# helloredis

This is a small project that consists of two components: A backend written in
python3, using FastAPI, and a frontend writting i python3, using Flask.
In addition, Redis is used for storing some data.

The goal of the project is to have these simple components to learn 
deployments in Kubernetes, including network, secrets, configmaps, and so on.

The frontend is a simple Flask webpage, which communicates via the backend
to store and retrieve information about hostname, first and last visit,
and number of visits. The data is stored in Redis.

There is separate directory for both frontend and backend, containg a README.md,
Dockerfile and the source code. And is this directory you will find an example
of a `docker-compose.yml` to test the code in a Docker environment.

