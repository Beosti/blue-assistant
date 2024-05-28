#!/bin/sh

# Install dependencies
pipenv install

# Run the bot script
pipenv run python server.py
