
#!/bin/bash

MONGO_DATABASE="AccessControl"
APP_NAME="AccessControl"

MONGO_HOST="127.0.0.1"
MONGO_PORT="27017"
TIMESTAMP=`date +%F-%H%M`
MONGODUMP_PATH="/usr/bin/mongodump"
BACKUPS_DIR="/home/pwings/backups/$APP_NAME"
BACKUP_NAME="$APP_NAME-$TIMESTAMP"

# mongo admin --eval "printjson(db.fsyncLock())"
# $MONGODUMP_PATH -h $MONGO_HOST:$MONGO_PORT -d $MONGO_DATABASE
$MONGODUMP_PATH -d $MONGO_DATABASE
# mongo admin --eval "printjson(db.fsyncUnlock())"

mkdir -p $BACKUPS_DIR
mv dump $BACKUP_NAME
tar -zcvf $BACKUPS_DIR/$BACKUP_NAME.tgz $BACKUP_NAME
rm -rf $BACKUP_NAME

#Message to Slack
if [ -f "$BACKUPS_DIR/$BACKUP_NAME.tgz" ]
then
    curl -X POST --data-urlencode 'payload={"channel": "#multiexportfoods", "username": "Multi-Boot", "text": "Automatic backup has completed successfully!", "icon_emoji": ":robot_face:"}' https://hooks.slack.com/services/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
else
    curl -X POST --data-urlencode 'payload={"channel": "#multiexportfoods", "username": "Multi-Boot", "text": "Automatic backup has *NOT completed*! :warning:", "icon_emoji": ":robot_face:"}' https://hooks.slack.com/services/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
fi
