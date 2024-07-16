#!/bin/bash


# Check if rabbit is up and running before starting the service.
until nc -z "${RABBIT_HOST:-rabbit}" "${RABBIT_PORT:-5672}"; do
  echo "$(date) - waiting for rabbitmq..."
  sleep 2
done

exec nameko run --config config.yml core.controller --backdoor-port 3000

