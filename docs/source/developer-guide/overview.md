# Technical Overview

## Tech Stack

### Frontend

The frontend is a Vue.js application built with [Quasar](https://quasar.dev/). It uses [Pinia](https://pinia.vuejs.org/) for state management and [Vue Router](https://router.vuejs.org/) for routing. It uses [Axios](https://axios-http.com/) for making HTTP requests to the backend. The app is built using [Vite](https://vitejs.dev/) and [TypeScript](https://www.typescriptlang.org/). When deployed, the static assets are served by Express (but with future plans to use Nginx for improved performance).

Other libraries used include:

- [TipTap](https://tiptap.dev/) for rich text editing
- [Plotly.js](https://plotly.com/javascript/) for rendering plots
- [Vanilla JSON Editor](https://www.npmjs.com/package/vanilla-jsoneditor) for editing the Plotly JSON data
- [VuePlyr](https://www.npmjs.com/package/vue-plyr) as a video player
- [VueUse](https://vueuse.org/) for various Vue utilities
- [JWT Decode](https://www.npmjs.com/package/jwt-decode) for decoding JWT tokens sent by the backend

### Backend

The backend is a Python application built with [FastAPI](https://fastapi.tiangolo.com/). It uses [Motor](https://motor.readthedocs.io), an async driver for MongoDB, for database operations. The [Minio SDK](https://github.com/minio/minio-py) as an S3 client. [Uvicorn](https://www.uvicorn.org/) is used as the ASGI server.

Other libraries used include:

- [Pydantic](https://pydantic-docs.helpmanual.io/) for data validation
- [Jinja2](https://jinja.palletsprojects.com/en/3.0.x/) for templating K8s manifests
- [Beautiful Soup](https://www.crummy.com/software/BeautifulSoup/bs4/doc/) for parsing HTML
- [Python JOSE](https://python-jose.readthedocs.io/en/latest/) for decoding JWT tokens sent by the frontend
- [Passlib](https://passlib.readthedocs.io/en/stable/) for hashing passwords
- [FastAPI CSRF Protect](https://pypi.org/project/fastapi-csrf-protect/) for CSRF protection
- [SSE Starlette](https://pypi.org/project/sse-starlette/) for Server Sent Events which are used for live updates of log data from a service to the front-end
- [ClearML SDK](https://pypi.org/project/clearml/) for interacting with ClearML

### Infrastructure

The application is deployed on [Kubernetes](https://kubernetes.io/). The backend and frontend are both K8S services, which are exposed externally using an [Nginx Ingress Controller](https://kubernetes.github.io/ingress-nginx/).

To host user applications, the backend uses [KNative Serving](https://knative.dev/docs/serving/). The ingress for KNative is configured to use [Kourier](https://knative.dev/docs/install/any-kubernetes-cluster/#installing-the-ingress). In the event that KNative is not available, the backend will fall back to using [Emissary Ingress](https://www.getambassador.io/docs/emissary/latest/topics/running/ingress-controller/), but will lose out on some of the features provided by KNative. (e.g Zero pod autoscaling)

## Project Structure

### Front End

```md
front-end
├── src/
│ ├── boot
│ ├── css
│ ├── components/
│ │ ├── content/
│ │ ├── editor/
│ │ ├── form/
│ │ ├── layout/
│ │ └── models.ts
│ ├── layouts
│ ├── pages
│ ├── plugins/tiptap-charts
│ ├── router
│ └── stores
├── test/
├── .env
├── Dockerfile
├── entrypoint.sh
├── package.json
├── package-lock.json
├── quasar.config.js
└── README.md
```

| File/Folder               | Description                                                                                                                                         |
| ------------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------- |
| src/boot                  | Contains files that are run before the app is mounted.                                                                                              |
| src/css                   | Contains global CSS files.                                                                                                                          |
| src/components/content    | Contains components that are used to display content.                                                                                               |
| src/components/editor     | Contains components that are used for the Tiptap editor.                                                                                            |
| src/components/form       | Contains components that are used for forms.                                                                                                        |
| src/components/layout     | Contains components that are used for layout (e.g Navbar).                                                                                          |
| src/components/models.ts  | Contains the interfaces for the data models used in the app.                                                                                        |
| src/layouts               | Contains the layouts for the app.                                                                                                                   |
| src/pages                 | Contains the pages for the app.                                                                                                                     |
| src/plugins/tiptap-charts | Contains the Tiptap extension for rendering charts.                                                                                                 |
| src/router                | Contains the Vue router for the app.                                                                                                                |
| src/stores                | Contains the Pinia stores for the app.                                                                                                              |
| test                      | Contains the tests for the app.                                                                                                                     |
| .env                      | Contains environment variables for the app. Values in there are usually placeholders that are replaced in production via real environment variables |
| Dockerfile                | Contains the Dockerfile for the app.                                                                                                                |
| entrypoint.sh             | Contains the entrypoint script for the app. This is used to dynamically replace variables (e.g back end URL) with environment variables             |
| package.json              | Contains the dependencies for the app.                                                                                                              |
| package-lock.json         | Contains the exact versions of the dependencies for the app.                                                                                        |
| quasar.config.js          | Contains the Quasar configuration for the app.                                                                                                      |
| README.md                 | Contains the README for the app.                                                                                                                    |

### Back End

```md
back-end
├── src/
│ ├── config/
│ │ ├── .env
│ │ ├── .env.gpg
│ │ ├── .env.public
│ │ ├── config.py
│ │ ├── decrypt-env.sh
│ │ └── encrypt-env.sh
│ ├── internal/
│ │ ├── data_connector/
│ │ ├── dependencies/
│ │ ├── experiment_connector/
│ │ ├── tasks/
│ │ ├── **init**.py
│ │ ├── auth.py
│ │ ├── preprocess_html.py
│ │ ├── templates.py
│ │ └── utils.py
│ ├── models/
│ ├── routers/
│ │ ├── auth.py
│ │ ├── buckets.py
│ │ ├── datasets.py
│ │ ├── engines.py
│ │ ├── experiments.py
│ │ ├── iam.py
│ │ └── models.py
│ ├── templates/
│ │ ├── ambassador/
│ │ └── knative/
│ ├── **init**.py
│ └── main.py
├── static
├── tests
├── CONTRIBUTING.md
├── Dockerfile
├── LICENSE
├── Makefile
├── poetry.lock
├── pyproject.toml
└── README.md
```

| File / Folder                      | Description                                                                                                                                                      |
| ---------------------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| src/config/.env                    | Contains environment variables for the app. This file is gitignored and should not be committed.                                                                 |
| src/config/.env.gpg                | Contains the encrypted .env file. This file is decrypted during CICD, with the GPG passphrase stored in the CICD secrets. (currently using symmetric encryption) |
| src/config/.env.public             | Contains placeholder environment variables for the app.                                                                                                          |
| src/config/config.py               | Contains the configuration for the app.                                                                                                                          |
| src/config/decrypt-env.sh          | Contains the script for decrypting the .env file.                                                                                                                |
| src/config/encrypt-env.sh          | Contains the script for encrypting the .env file.                                                                                                                |
| src/internal/data_connector/       | Contains the data connectors for the app.                                                                                                                        |
| src/internal/experiment_connector/ | Contains the experiment connectors for the app.                                                                                                                  |
| src/internal/dependencies/         | Contains the dependencies for the app.                                                                                                                           |
| src/internal/tasks/                | Contains the background tasks for the app.                                                                                                                       |
| src/internal/**init**.py           | Contains the initialization for the internal package.                                                                                                            |
| src/internal/auth.py               | Contains the authentication for the app.                                                                                                                         |
| src/internal/preprocess_html.py    | Contains the HTML preprocessor for the app.                                                                                                                      |
| src/internal/templates.py          | Contains the Jinja template generator for the app.                                                                                                               |
| src/internal/utils.py              | Contains the utility functions for the app.                                                                                                                      |
| src/models/                        | Contains the Pydantic data models for the app.                                                                                                                   |
| src/routers/                       | Contains the router and controllers for the app.                                                                                                                 |
| src/templates/                     | Contains the Jinja templates for the app.                                                                                                                        |
| src/**init**.py                    | Contains the initialization for the app.                                                                                                                         |
| src/main.py                        | Contains the main entrypoint for the app.                                                                                                                        |
| static/                            | Contains the static files for the app.                                                                                                                           |
| tests/                             | Contains the tests for the app.                                                                                                                                  |
| CONTRIBUTING.md                    | Contains the contributing guidelines for the app.                                                                                                                |
| Dockerfile                         | Contains the Dockerfile for the app.                                                                                                                             |
| LICENSE                            | Contains the license for the app.                                                                                                                                |
| Makefile                           | Contains the Makefile for the app.                                                                                                                               |
| poetry.lock                        | Contains the exact versions of the dependencies for the app.                                                                                                     |
| pyproject.toml                     | Contains the dependencies for the app.                                                                                                                           |
| README.md                          | Contains the README for the app.                                                                                                                                 |

## Contributing

### Setup Development Environment

To setup your dev environment, please check the following guides:

- [Setup Dev Tools](setup-dev-environment/development-tools.md)
- [Setup Front End](setup-dev-environment/setting-up-front-end.md)
- [Setup Back End](setup-dev-environment/setting-up-back-end.md)

### Style Guide

#### Git Commit Messages

The style of Git commit messages is as follows:
`[<tag>] <message>`
Where `<tag>` is one of the following:

- `feat` - A new feature
- `fix` - A bug fix
- `refactor` - A code change that neither fixes a bug nor adds a feature
- `docs` - Documentation only changes
- `test` - Adding missing tests or correcting existing tests
- `version` - Version bump
- `dbg` - Debugging
- `hack` - Quick and dirty code
- `wip` - Work in progress
- `config` - Configuration changes

To make it easier to adhere to this style, we have provided a Git commit template in the `.github` folder. To use it, run the following command:

```bash
git config commit.template .github/ct.md
```

<!-- TODO: Consider moving to Conventional Commits Style in Future? -->
<!-- TODO: Use commitlint to ensure contributors adhere to commit format? -->

#### Back End

The Python code is formatted using [Black](https://github.com/psf/black) and [isort](https://pycqa.github.io/isort/).

To format code using Black, run the following command:

```bash
black .
```

To format code using isort, run the following command:

```bash
isort .
```

<!-- TODO: Better enforce code style by checking that code is formatted in CI pipeline -->

#### Front End

Code formatting is enforced using [Prettier](https://prettier.io/). To format code, run the following command:

```bash
npm run format
```
