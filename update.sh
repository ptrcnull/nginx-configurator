#!/bin/bash
docker-compose down
git pull && node generate.js && docker-compose up -d
