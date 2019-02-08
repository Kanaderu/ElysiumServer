#!/bin/bash

BACKUP_FILE=ES.backup

# backup database
pg_dump $DB_NAME -U $DB_USER > $BACKUP_FILE
