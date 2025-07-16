#!/usr/bin/env bash
set -e

# 1.  Load the .env that sits right beside this script
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
if [ -f "${SCRIPT_DIR}/.env" ]; then
  set -o allexport
  source "${SCRIPT_DIR}/.env"
  set +o allexport
else
  echo "❌  ${SCRIPT_DIR}/.env not found — aborting."
  exit 1
fi

# From .env file
ICLOUD_DIR="$ICLOUD_DIR"
LOCAL_DIR="$LOCAL_DIR"

# Change to the user directory where Docker can run
cd "$LOCAL_DIR"

# Create logs directory if it doesn't exist
mkdir -p logs

# If no arguments, default to "up -d"
if [ $# -eq 0 ]; then
  COMPOSE_ARGS="up -d"
else
  COMPOSE_ARGS="$*"
fi

# Determine mode: silent for up -d (including default), verbose otherwise
if [ $# -eq 0 ] || echo "$COMPOSE_ARGS" | grep -qE '(^| )up -d($| )'; then
  # Silent mode: kill previous log-followers, run detached, write only to log files
  pkill -f "docker logs -f" 2>/dev/null || true
  docker compose \
    -f "$ICLOUD_DIR/docker-compose.yaml" \
    --env-file "$ICLOUD_DIR/.env" \
    $COMPOSE_ARGS > logs/docker-compose.log 2>&1
  # Silent mode: start container logs in background, writing only to files
  for svc in postgres_db metabase metabase_setup; do
    docker logs -f $svc > logs/${svc}.log 2>&1 &
  done
else
  # Verbose mode: append new logs to existing files and print to terminal
  docker compose \
    -f "$ICLOUD_DIR/docker-compose.yaml" \
    --env-file "$ICLOUD_DIR/.env" \
    $COMPOSE_ARGS 2>&1 | tee -a logs/docker-compose.log
fi

# Verbose mode: append new logs to log files and display them
if [ $# -ne 0 ] && echo "$COMPOSE_ARGS" | grep -qE '(^| )up($| )'; then
  for svc in postgres_db metabase metabase_setup; do
    docker logs -f $svc 2>&1 | tee -a logs/${svc}.log &
  done
fi
