#!/bin/bash

if [ -z "$1" ] && [ -z "$WANDB_API_KEY" ]; then
  echo "Usage: $0 <WANDB_API_KEY>"
  echo "Or set the WANDB_API_KEY environment variable before running the script."
  exit 1
fi

if [ -n "$1" ]; then
  WANDB_API_KEY=$1
fi

echo "Running the app"
echo "Setting up the environment variables"
echo "WANDB_API_KEY: $WANDB_API_KEY"

export WANDB_API_KEY=$WANDB_API_KEY

docker-compose up
