#!/bin/bash

BACKUP_FILE=ES.backup

# restore database
psl $DB_NAME -U $DB_USER < $BACKUP_FILE
