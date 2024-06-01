#!/bin/sh

# Install dependencies
pipenv install discord.py
pipenv install python-dotenv

# Run the bot script
pipenv run python server.py
