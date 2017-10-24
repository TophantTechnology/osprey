#!/bin/bash

cd web/

# Start the osprey-web
gunicorn -b 0.0.0.0:5000 osprey-web:app -w 5 -D
status=$?
if [ $status -ne 0 ]; then
  echo "Failed to start osprey web: $status"
  exit $status
fi

# Start the osprey workers
nohup celery -A osprey-web.celery worker --concurrency=5 -Q poc-queue -n osprey.%h -Ofair &
status=$?
if [ $status -ne 0 ]; then
  echo "Failed to start osprey workers: $status"
  exit $status
fi

# Naive check runs checks once a minute to see if either of the processes exited.
# This illustrates part of the heavy lifting you need to do if you want to run
# more than one service in a container. The container will exit with an error
# if it detects that either of the processes has exited.
# Otherwise it will loop forever, waking up every 60 seconds

while /bin/true; do
  ps aux | grep gunicorn | grep -q -v grep
  osprey_web=$?
  ps aux | grep celery | grep -q -v grep
  osprey_worker=$?
  # If the greps above find anything, they will exit with 0 status
  # If they are not both 0, then something is wrong
  if [ $osprey_web -ne 0 -o $osprey_worker -ne 0 ]; then
    echo "One of the processes has already exited."
    exit -1
  fi
  sleep 60
done
