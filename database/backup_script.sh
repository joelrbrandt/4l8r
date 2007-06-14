#! /bin/bash
DATASTORE_DIR="/4l8r"
BACKUP_DIR="/4l8r-backup"

REMOTE_LOCATION="blit.stanford.edu:4l8r-backup"
REMOTE_USER="jbrandt"
REMOTE_USER_KEYFILE="/4l8r-backup/4l8r-backup-keyfile"

DATABASE_NAME="forlater"
DATABASE_USER="forlater-backup"

DATE=`date +%F`

cd $BACKUP_DIR

mkdir $DATE
cp -r $DATASTORE_DIR/* $DATE

mysqldump -u $DATABASE_USER $DATABASE_NAME > $DATE/database.sql

zip -q -r $DATE.zip $DATE

rm -rf $DATE

scp -q -i $REMOTE_USER_KEYFILE $DATE.zip $REMOTE_USER@$REMOTE_LOCATION