# GSCS (Ground Station Central Server)

GSCS es un servidor que recibe datos en crudo de la Estación Terrestre Óptica (OGS), los convierte, descifra, almacena y verifica errores. También se comunica con el Satélite (SAT) y la Estación Terrestre de Radio (RGS). Utiliza un sistema de doble buffer para optimizar el procesamiento y garantizar la sincronización de datos en un tiempo máximo de 1 hora.

## Características principales

- Procesamiento automático de datos en segundo plano.

- Comunicación con OGS, SAT y RGS.

- Doble buffer para eficiencia.

- Apuntado Inicial (ApIni) y Detección y Tracking (DyT).

- Backend basado en Django Ninja.

- API para acceso a datos procesados.

## Requisitos

Asegúrate de tener instalado:

- Docker

- Docker Compose

## Instalación y ejecución

Para ejecutar el proyecto con Docker Compose, sigue estos pasos:

1. Clona el repositorio:

```bash
git clone https://github.com/Teidesat/ground-stations-central-server.git
```

2. Crea un archivo .env con las variables necesarias (si aplica).

3. Construye y levanta los contenedores:

```bash
docker-compose up --build
```

4. Para detener los contenedores:

```bash
docker-compose down
```

5. Para correr en segundo plano:

```bash
docker-compose up -d
```


## Licencia

Este proyecto está bajo la licencia GPL-3.0.

