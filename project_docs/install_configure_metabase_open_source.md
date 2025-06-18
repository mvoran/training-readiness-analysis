# Install and Configure Metabase Open Source Using Postgres on Local Instance

## Install Docker Desktop
1. Get download file from here: https://docs.docker.com/desktop/release-notes/. The correct version for a MacBook Air is *Mac with Apple Chip*.
2. Follow installation instructions found here: https://docs.docker.com/desktop/setup/install/mac-install/.

> [!NOTE]
> To download images I had to `docker logout` followed by `docker login` (with username and password) to clear a 401 error.

## Download Metabase Open Source
> [!NOTE]
> Running `docker pull metabase/metabase:latest` won't necessarily work as **latest** may not have an **arm64** version.

1. Find the latest version arm64 version here: https://hub.docker.com/r/metabase/metabase/tags.
2. In the `docker-compose.yaml` file update the metabase **image** tag, e.g., `metabase/metabase:v0.55.4.1`.

## Configure Metabase
> [!NOTE]
> Docker Desktop does not allow running Docker Compose files from arbitrary locations. however, it does allow these files to run from a user directory, e.g., `/users/<user_name>`. Since my repo lives in iCloud, and since the Docker compose setup requires multiple files, I decided to run Docker Compose via an .sh file. The .sh file relies on an .env file for path information, so I have to sync the .sh and .env files in the user directory to the repo, but that is still better than managing five separate files to run Docker Compose.

> [!TIP]
> When you start, your Docker directory in iCloud should look something like this:
 ``` .
 ├── database
 └── docker
    ├── .env
    ├── docker-compose.yaml
    ├── env.template
    ├── init-training.sql
    ├── metabase-setup.sh
    └── run_docker.sh
 ```

1. Update the .env file with the location of the iCloud project directory along with the local Users directory that will hold the .sh and .env files.
2. Copy the `run_docker.sh` and `.env` files to the specified location in your Users directory.
3. When done, your Users directory should look something like this:
```
.
└── Training_Readiness
    ├── .env
    ├── logs
    │   ├── docker-compose.log
    │   ├── metabase_setup.log
    │   ├── metabase.log
    │   └── postgres_db.log
    └── run_docker.sh
```
4. Start Docker Compose by running `./run_docker.sh up -d`.
5. You can bring down Docker Compose by running `./run_docker.sh down -v`.
6. It will take a minute or two to launch Metabase, configure the Postges database, etc.
7. To start Metabase browse to `http://localhost:3000`.
8. Enter your username and password.
9. At this point you should have a running instance of Metabase Open Source and a configured Postgres database.


