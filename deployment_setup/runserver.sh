#!/bin/bash

# launch server with uwsgi
sudo -E `which uwsgi` --http :80 --module ElysiumServer.wsgi
