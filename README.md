# helloredis

A simple Flask webpage using redis to track hostname, first and last visit, and number of visits. The idea is to run one Redis-server and multiple webapps in the Kubernetes cluster.
This part also contains a `Dockerfile` and `docker-compose.yml` to create the container and verify it using Docker.

The Docker images built are hosted on my public repo at Docker Hub: https://hub.docker.com/r/sitronno/redishello

#### Notes

- I use the `bullseye` and `buster` version of python3-slim and redis Docker images, since my Kubernetes lab consists of Raspberry Pi's, running Raspbian 10.
- To build and upload multi-arch images to Docker Hub, use [buildx](https://github.com/docker/buildx): `docker buildx build --push --platform linux/arm/v7,linux/amd64 --tag sitronno/redishello:v1.0 .`
- This was part of my [k8s-n00b](https://github.com/SitronNO/k8s-n00b) project, but k8s-n00b is no longer under maintenance.
