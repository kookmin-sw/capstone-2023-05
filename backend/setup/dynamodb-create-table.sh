#!/bin/bash

aws dynamodb create-table \
    --table-name ws-connection \
    --attribute-definitions \
        AttributeName=battleID,AttributeType=S \
        AttributeName=connectionID,AttributeType=S \
    --key-schema \
        AttributeName=battleID,KeyType=HASH \
        AttributeName=connectionID,KeyType=RANGE \
    --provisioned-throughput \
        ReadCapacityUnits=5,WriteCapacityUnits=5 \
    --endpoint-url http://localhost:8000