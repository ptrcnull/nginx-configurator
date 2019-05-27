#!/bin/bash
source clean.sh
docker-compose down
git pull && node generate.js && docker-compose up -d
