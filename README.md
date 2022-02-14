# Setae API

API middleware to support LTS workflows in FOLIO.

## Prerequisites

- [Docker](https://docs.docker.com/get-docker/)
  > If using Docker Desktop, [ensure filesystem sharing for macOS](https://docs.docker.com/desktop/mac/#file-sharing) or [shared drives for Windows](https://docs.docker.com/desktop/windows/#file-sharing) is configured properly to support mounting files at the path of your working copy for this repo.
- [Docker Compose](https://docs.docker.com/compose/install/)
- FOLIO user account with necessary permissions
  > see [folio-permset.json](folio-permset.json)

## Dev Quickstart

1. Clone this repo

   ```sh
   git clone git@github.com:cul-it/setae-api.git
   cd setae-api
   ```

1. Setup environment variables

   ```sh
   cp .env.example .env
   ```
   > Replace **CHANGEME** placeholders in `.env` with appropriate values

1. Build the Docker Image

   ```sh
   docker-compose build
   ```

1. Start the Dev Environment

    ```sh
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

## `/items/{barcode}` endpoint for SpineOMatic spine labeler

Submit a `GET` request to the http://localhost/items/{barcode} using the barcode of a known item in your FOLIO tenant. This will return XML ready to be consumed by [SpineOMatic](https://github.com/ExLibrisGroup/SpineOMatic).

> Review the [SpineOMatic wiki](https://github.com/ExLibrisGroup/SpineOMatic/wiki/Quick-Start-Guide----Installation) for installation and settings documentation. More specific details on configuring SpineOMatic to use this FOLIO API middleware will be provided here in the near future.

You can request the original, unmodified JSON from FOLIO using the `format` parameter:

http://localhost/items/{barcode}?format=json

> Refer to the generated [API documentation for the /items endpoint](http://localhost/docs#/default/read_item_items__barcode__get) for all available parameters
