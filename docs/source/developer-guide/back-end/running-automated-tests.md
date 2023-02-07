# Running Automated Tests

To run automated tests, we have set up a docker-compose file that will allow you to run the tests in a container, along with any potentially required dependencies (e.g Minio). To run the tests, run the following command:

```bash
cd tests
docker compose up
docker exec -it back-end-tests-backend-1 bash
```

This will start up the tests container, and then you can run the tests inside the container. To run the tests, run the following command:

```bash
poetry run pytest
```

## Note

While you could run the tests locally, we recommend that you run the tests in a container, as the config system right now is somewhat wonky and will not work properly if you run the tests locally, since it will try to use the development config instead of the test config.
