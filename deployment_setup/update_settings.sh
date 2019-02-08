#!/bin/bash

COMMAND=(flush makemigrations migrate)
MODULE=(ElysiumServer.settings.production ElysiumServer.settings.dev)

python manage.py ${COMMAND[1]} --settings ${MODULE[0]}
