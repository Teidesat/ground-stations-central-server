# GSCS (Ground Station Central Server)

![django 5.1](https://img.shields.io/badge/django-5.1.7-blue)
![django ninja 1.3](https://img.shields.io/badge/1.3-blue?color=blue&label=django-ninja&logo=fastapi&logoColor=white)
![PostgreSQL 17](https://img.shields.io/badge/PostgreSQL-17-blue?logo=postgresql&logoColor=white)
![TimescaleDB](https://img.shields.io/badge/TimescaleDB-pg16-orange?logo=timescale&logoColor=white)
[![License: GPL v3](https://img.shields.io/badge/License-GPLv3-green.svg)](https://www.gnu.org/licenses/gpl-3.0)
![Version](https://img.shields.io/badge/alpha-0.0.0-yellow.svg)

> From TEIDESAT Project and Hyperspace Canarias

## Description

GSCS is a server that receives raw data from the Optical Ground Station (OGS), converts, decrypts, stores, and verifies errors. It also communicates with the Satellite (SAT) and the Radio Ground Station (RGS). It uses a double buffer system to optimize processing and ensure data synchronization within a maximum time of 1 hour, supported by a dual-database architecture (PostgreSQL + TimescaleDB) and decoupled filesystem storage for satellite images.

## Main Features

- Automatic background data processing (Celery, Redis, and Flower).

- Communication with OGS, SAT, and RGS.

- Double buffer for efficiency.

- Hybrid database architecture: PostgreSQL 17 for relational data and TimescaleDB for high-frequency satellite telemetry.

- Decoupled multimedia storage on the local filesystem (`media/images/`).

- Backend based on Django Ninja.

- API for accessing processed data.

## Requirements

Make sure you have installed:

- Docker

- Docker Compose

## Installation and Execution

To run the project with Docker Compose, follow these steps:

1. Clone the repository:

```bash
git clone [https://github.com/Teidesat/ground-stations-central-server.git](https://github.com/Teidesat/ground-stations-central-server.git)
```

2. Create a .env file with the necessary variables (if applicable).

3. Build and start the containers:

```bash
docker compose up --build
```

4. Apply migrations for both databases (first time only):

```bash
docker compose exec app python manage.py migrate
docker compose exec app python manage.py migrate --database=timescale
```

5. To stop the containers:

```bash
docker compose down
```

6. To run in the background:

```bash
docker compose up -d
```

7. For try api endpoints:
   <br>
   <a href="http://localhost:8000/api/docs"> Click here to check endpoints</a>

## Testing

For detailed instructions on running tests, see the [Testing Guide](/tests/test.md)

## Documentación extensa
<a href="https://deepwiki.com/Teidesat/ground-stations-central-server/1-overview"> Aquí la documentación en inglés</a>


## License

This project is licensed under GPL-3.0.
