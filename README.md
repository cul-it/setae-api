# Setae API

API middleware to support LTS workflows in FOLIO.

## Dev Quickstart

### Prerequisites

* [Docker](https://docs.docker.com/install/)
* [Docker Compose](https://docs.docker.com/compose/install/)

> If using Docker Desktop, [ensure filesystem sharing for macOS](https://docs.docker.com/docker-for-mac/osxfs/#namespaces) or [shared drives for Windows](https://docs.docker.com/docker-for-windows/#shared-drives) is configured properly to support mounting files at the path of your working copy for this repo.

### Clone this repo

```
git clone git@github.com:cul-it/setae-api.git
cd setae-api
```

### Configure Environment Variables

```
cp .env.example .env
```
> Replace all instances of `CHANGEME` with appropriate values

### Build the Docker Image

```
docker-compose build
```

### Start the Dev Environment

 ```
 docker-compose up
 ```

Once the dev environment has started, the API should be running at http://localhost. 

> You can visit the generated API documentation at http://localhost/docs.

### Stopping the Dev Environment

```
docker-compose down
```
> If running in the foreground, simply press `CTRL + C`


### Running arbitrary commands

* Get a shell into your running application container
  ```
  docker-compose exec api bash
  ```
