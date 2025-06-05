# Install and Configure Metabase Open Source Using Postgres on Local Instance #

## Install Docker Desktop ##
1. Get download file from here: https://docs.docker.com/desktop/release-notes/. The correct version for a MacBook Air is *Mac with Apple Chip*.
2. Follow installation instructions found here: https://docs.docker.com/desktop/setup/install/mac-install/.

*Note*: To download images I had to `docker logout` followed by `docker login` (with username and password) to clear a 401 error.

## Download Metabase Open Source ##
*Note*: running `docker pull metabase/metabase:latest` won't necessarily work as **latest** may not have an **arm64** version.

1. Find the latest version arm64 version here: https://hub.docker.com/r/metabase/metabase/tags.
2. From Docker Desktop open Terminal and pull the Docker image, e.g., `docker pull metabase/metabase:v0.55.1`.
3. Run the Docker image, e.g.,: `docker run -d --name metabase -p 3000:3000 \metabase/metabase:v0.55.1`.
    1. Note that if you are running a version other than **latest** you need to include the tag.
