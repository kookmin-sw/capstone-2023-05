#!/bin/bash

aws dynamodb --endpoint-url http://localhost:8000 \
    create-table \
    --table-name ws-connections \
    --attribute-definitions \
        AttributeName=battleID,AttributeType=S \
        AttributeName=connectionID,AttributeType=S \
    --key-schema \
        AttributeName=battleID,KeyType=HASH \
        AttributeName=connectionID,KeyType=RANGE \
    --provisioned-throughput \
        ReadCapacityUnits=5,WriteCapacityUnits=5 \
    --endpoint-url http://localhost:8000