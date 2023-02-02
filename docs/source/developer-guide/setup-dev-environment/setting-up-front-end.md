# Setting Up Front End

## Pre-requisites

You will need to have the following installed:

- [Node.js](https://nodejs.org/en/download/package-manager/) (version 16 or higher)

See [Setting Up Development Tools](development-tools.md#installing-nodejs) for more information on setting up your development environment.

## Installing Quasar

Quasar is a framework for building Vue.js applications. It is used to build the front end of the project and provides a Vite based CLI tool to aid in development and building of the app. Install Quasar CLI from [here](https://quasar.dev/start/quasar-cli/).

## Installing Dependencies

First, go to the `front-end` directory:

```bash
cd front-end
```

Then, install the dependencies:

```bash
npm install
```

The core dependencies are:

- Vue.js: a JavaScript framework for building user interfaces
- Quasar: a framework for building Vue.js applications
- Pinia: a state management library for Vue.js
- Vue Router: a routing library for Vue.js
- Axios: a library for making HTTP requests

## Running the App

To run the app in development mode, run:

```bash
quasar dev
```

This will start a development server on port 8080. You can access the app at `http://localhost:8080`.
