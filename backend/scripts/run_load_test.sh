#!/bin/bash

# Default values
USERS=10
SPAWN_RATE=1
RUNTIME=60
HOST="http://localhost:8000"

# Parse command line arguments
while [[ $# -gt 0 ]]; do
  case $1 in
    --users)
      USERS="$2"
      shift 2
      ;;
    --spawn-rate)
      SPAWN_RATE="$2"
      shift 2
      ;;
    --runtime)
      RUNTIME="$2"
      shift 2
      ;;
    --host)
      HOST="$2"
      shift 2
      ;;
    *)
      echo "Unknown option: $1"
      exit 1
      ;;
  esac
done

echo "Starting load test with:"
echo "Users: $USERS"
echo "Spawn rate: $SPAWN_RATE"
echo "Runtime: $RUNTIME seconds"
echo "Host: $HOST"

# Run the load test
locust \
  --host $HOST \
  --users $USERS \
  --spawn-rate $SPAWN_RATE \
  --run-time ${RUNTIME}s \
  --headless \
  --only-summary \
  -f ../tests/load_test.py 